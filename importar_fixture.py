import os
import django
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mundial_prode.settings')
django.setup()

from core.models import Partido

API_TOKEN = os.getenv('API_TOKEN')
# ID 2021 = Premier League
API_URL = "https://api.football-data.org/v4/competitions/2021/matches"
HEADERS = {'X-Auth-Token': API_TOKEN}

def importar_partidos():
    print(f"--- INICIANDO IMPORTACIÓN ROBUSTA ---")
    
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        partidos_api = data.get('matches', [])
        
        print(f"Procesando {len(partidos_api)} partidos...")

        for match in partidos_api:
            api_id = str(match['id'])
            numero_fecha = match.get('matchday', 1)
            fecha_str = match['utcDate']
            fecha_hora = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%SZ")
            
            # Datos del Local
            id_local = match['homeTeam']['id']
            equipo_local = match['homeTeam']['name']
            
            # --- TRUCO: Si no viene el escudo, lo fabricamos con el ID ---
            escudo_local = match['homeTeam'].get('crest')
            if not escudo_local:
                escudo_local = f"https://crests.football-data.org/{id_local}.png"
            
            # Datos del Visitante
            id_visitante = match['awayTeam']['id']
            equipo_visitante = match['awayTeam']['name']
            
            # --- Mismo truco para el visitante ---
            escudo_visitante = match['awayTeam'].get('crest')
            if not escudo_visitante:
                escudo_visitante = f"https://crests.football-data.org/{id_visitante}.png"

            # Estado del partido
            status = match['status']
            jugado = status in ['FINISHED', 'IN_PLAY'] 
            
            goles_local = None
            goles_visitante = None
            
            if jugado and match['score']['fullTime']['home'] is not None:
                 goles_local = match['score']['fullTime']['home']
                 goles_visitante = match['score']['fullTime']['away']

            # Guardamos en BD
            Partido.objects.update_or_create(
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
            
        print("✅ ¡Listo! Partidos importados con escudos forzados.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    importar_partidos()