#!/bin/bash
# Script bash para ejecutar desde PythonAnywhere Scheduled Tasks
# Asegúrate de ajustar las rutas según tu configuración

cd /home/tu_usuario/mundial_prode  # Cambia 'tu_usuario' por tu usuario de PythonAnywhere
source /home/tu_usuario/.virtualenvs/mundial_prode/bin/activate  # Si usas virtualenvwrapper
# O si usas un venv en el proyecto:
# source venv/bin/activate

python manage.py actualizar_resultados
