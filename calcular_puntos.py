import os
import django
from django.db.models import Sum

# Configuración inicial de Django para correr como script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mundial_prode.settings')
django.setup()

from core.models import Partido, Pronostico, PerfilEmpleado

def calcular_puntos():
    print("--- INICIANDO CÁLCULO DE PUNTOS ---")
    
    # 1. Buscamos solo los partidos que YA SE JUGARON y tienen resultado cargado
    partidos_jugados = Partido.objects.filter(jugado=True)
    
    print(f"Procesando {partidos_jugados.count()} partidos jugados...")

    for partido in partidos_jugados:
        # Obtenemos todos los pronósticos hechos para ese partido
        pronosticos = Pronostico.objects.filter(partido=partido)
        
        real_local = partido.goles_local_real
        real_visitante = partido.goles_visitante_real

        for pron in pronosticos:
            pred_local = pron.goles_local_prediccion
            pred_visitante = pron.goles_visitante_prediccion
            
            puntos = 0

            # A) ¿Acertó el resultado EXACTO? (Ej: Dijo 2-1 y fue 2-1)
            if real_local == pred_local and real_visitante == pred_visitante:
                puntos = 3 
            
            # B) Si no fue exacto, ¿acertó al menos quién ganaba?
            else:
                # Verificamos quién ganó en la realidad
                gano_local_real = real_local > real_visitante
                gano_visita_real = real_visitante > real_local
                empate_real = real_local == real_visitante
                
                # Verificamos quién ganó en la predicción
                gano_local_pred = pred_local > pred_visitante
                gano_visita_pred = pred_visitante > pred_local
                empate_pred = pred_local == pred_visitante
                
                # Si coinciden los escenarios, suma 1 punto
                if (gano_local_real and gano_local_pred) or \
                   (gano_visita_real and gano_visita_pred) or \
                   (empate_real and empate_pred):
                    puntos = 1
            
            # Guardamos los puntos en ese pronóstico específico
            if pron.puntos_ganados != puntos:
                pron.puntos_ganados = puntos
                pron.save()
    
    # 2. Actualizar la Tabla de Posiciones (Suma total por usuario)
    print("Actualizando Ranking de Usuarios...")
    perfiles = PerfilEmpleado.objects.all()
    
    for perfil in perfiles:
        # Sumamos la columna 'puntos_ganados' de todos sus pronósticos
        resultado = Pronostico.objects.filter(usuario=perfil.usuario).aggregate(Sum('puntos_ganados'))
        total = resultado['puntos_ganados__sum']
        
        # Si no tiene puntos (None), le ponemos 0
        if total is None:
            total = 0
            
        perfil.puntos_totales = total
        perfil.save()
        print(f" > {perfil.usuario.username}: {total} pts")

    print("--- CÁLCULO FINALIZADO ---")

if __name__ == "__main__":
    calcular_puntos()