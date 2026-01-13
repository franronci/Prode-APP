#!/usr/bin/env python
"""
Script para ejecutar desde PythonAnywhere Scheduled Tasks.
Actualiza los resultados de los partidos desde la API de Football Data.
"""
import os
import sys
import django
from pathlib import Path

# Configurar el path de Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mundial_prode.settings')
django.setup()

# Ahora podemos ejecutar el comando
from django.core.management import call_command

if __name__ == '__main__':
    try:
        call_command('actualizar_resultados')
    except Exception as e:
        print(f"Error ejecutando el comando: {e}")
        sys.exit(1)
