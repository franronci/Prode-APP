from django.contrib import admin
from .models import Partido, Pronostico, PerfilEmpleado, Empresa

# 1. Configuración para los Partidos
@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    # Qué columnas ver en la lista
    list_display = ('numero_fecha', 'fecha_hora', 'equipo_local', 'goles_local_real', 'goles_visitante_real', 'equipo_visitante', 'jugado')
    
    # Filtros laterales (¡Súper útil!)
    list_filter = ('numero_fecha', 'jugado')
    
    # Buscador por nombre de equipos
    search_fields = ('equipo_local', 'equipo_visitante')
    
    # Ordenar por defecto
    ordering = ('numero_fecha', 'fecha_hora')
    
    # ¡TRUCO! Permitir editar el resultado DIRECTAMENTE desde la lista
    list_editable = ('goles_local_real', 'goles_visitante_real', 'jugado')
    list_per_page = 20

# 2. Configuración para los Pronósticos
@admin.register(Pronostico)
class PronosticoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'partido', 'goles_local_prediccion', 'goles_visitante_prediccion', 'puntos_ganados')
    list_filter = ('usuario', 'puntos_ganados')
    search_fields = ('usuario__username', 'partido__equipo_local', 'partido__equipo_visitante')

# 3. Configuración para el Perfil (Ranking)
@admin.register(PerfilEmpleado)
class PerfilEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'puntos_totales')
    list_filter = ('empresa',)
    search_fields = ('usuario__username', 'empresa__nombre')
    ordering = ('-puntos_totales',) # Ordenar por quien va ganando

# 4. Configuración simple para Empresa
admin.site.register(Empresa)