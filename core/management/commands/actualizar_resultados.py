import os
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Partido

# Intentar cargar dotenv si está disponible (opcional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Si no está instalado, continuar sin él

class Command(BaseCommand):
    help = 'Consulta la API y actualiza los resultados de los partidos jugados'

    def handle(self, *args, **kwargs):
        self.stdout.write("📡 Conectando con la API de fútbol...")
        
        # Obtener token de la API desde variables de entorno
        API_TOKEN = os.getenv('API_TOKEN')
        if not API_TOKEN:
            self.stdout.write(self.style.ERROR('❌ Error: API_TOKEN no configurado en variables de entorno'))
            return
        
        # ID 2021 = Premier League (ajusta según tu competencia)
        API_URL = "https://api.football-data.org/v4/competitions/2021/matches"
        HEADERS = {'X-Auth-Token': API_TOKEN}
        
        try:
            response = requests.get(API_URL, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            partidos_api = data.get('matches', [])
            
            self.stdout.write(f"Procesando {len(partidos_api)} partidos de la API...")
            
            partidos_actualizados = 0
            partidos_nuevos = 0
            
            for match in partidos_api:
                api_id = str(match['id'])
                numero_fecha = match.get('matchday', 1)
                fecha_str = match['utcDate']
                fecha_hora = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%SZ")
                
                # Datos de equipos
                equipo_local = match['homeTeam']['name']
                equipo_visitante = match['awayTeam']['name']
                
                # Escudos
                id_local = match['homeTeam']['id']
                escudo_local = match['homeTeam'].get('crest')
                if not escudo_local:
                    escudo_local = f"https://crests.football-data.org/{id_local}.png"
                
                id_visitante = match['awayTeam']['id']
                escudo_visitante = match['awayTeam'].get('crest')
                if not escudo_visitante:
                    escudo_visitante = f"https://crests.football-data.org/{id_visitante}.png"
                
                # Estado y resultado
                status = match['status']
                jugado = status in ['FINISHED', 'IN_PLAY']
                
                goles_local = None
                goles_visitante = None
                
                if jugado and match['score']['fullTime']['home'] is not None:
                    goles_local = match['score']['fullTime']['home']
                    goles_visitante = match['score']['fullTime']['away']
                
                # Usar update_or_create para evitar duplicados
                partido, creado = Partido.objects.update_or_create(
                    api_id=api_id,
                    defaults={
                        'numero_fecha': numero_fecha,
                        'equipo_local': equipo_local,
                        'escudo_local': escudo_local,
                        'equipo_visitante': equipo_visitante,
                        'escudo_visitante': escudo_visitante,
                        'fecha_hora': fecha_hora,
                        'jugado': jugado,
                        'goles_local_real': goles_local,
                        'goles_visitante_real': goles_visitante,
                    }
                )
                
                if creado:
                    partidos_nuevos += 1
                    self.stdout.write(self.style.WARNING(f"➕ Nuevo partido creado: {partido}"))
                else:
                    partidos_actualizados += 1
            
            self.stdout.write(self.style.SUCCESS(
                f"🏁 Proceso finalizado. Actualizados: {partidos_actualizados}, Nuevos: {partidos_nuevos}"
            ))
            self.stdout.write("💡 Los puntos se calcularon automáticamente gracias a los signals de Django.")
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Error al conectar con la API: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error inesperado: {e}"))