import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

# --- MODELO EMPRESA ---
class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_acceso = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre

# --- MODELO PERFIL DE EMPLEADO (Ranking) ---
class PerfilEmpleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    puntos_totales = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.puntos_totales} pts"

# --- MODELO PARTIDO ---
class Partido(models.Model):
    equipo_local = models.CharField(max_length=50)
    equipo_visitante = models.CharField(max_length=50)
    escudo_local = models.URLField(blank=True, null=True)     # URL de imagen
    escudo_visitante = models.URLField(blank=True, null=True) # URL de imagen
    
    fecha_hora = models.DateTimeField()
    numero_fecha = models.IntegerField() # Ej: Fecha 1, Fecha 2...
    
    # Resultado Real (Lo carga el admin después)
    goles_local_real = models.IntegerField(blank=True, null=True)
    goles_visitante_real = models.IntegerField(blank=True, null=True)
    jugado = models.BooleanField(default=False)

    def __str__(self):
        return f"Fecha {self.numero_fecha}: {self.equipo_local} vs {self.equipo_visitante}"

# --- MODELO PRONÓSTICO (La apuesta del usuario) ---
class Pronostico(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    
    goles_local_prediccion = models.IntegerField()
    goles_visitante_prediccion = models.IntegerField()
    
    puntos_ganados = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('usuario', 'partido') # Un usuario no puede apostar 2 veces al mismo partido

    def __str__(self):
        return f"{self.usuario} - {self.partido}"

# --- MODELO TORNEO (Ligas de amigos) ---
class Torneo(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True, editable=False)
    participantes = models.ManyToManyField(User, related_name='torneos_participados')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='torneos_creados')

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = str(uuid.uuid4()).replace('-', '')[:6].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


# --- AUTOMATIZACIÓN DE PUNTOS (SIGNALS) ---
# Esto corre automáticamente cada vez que el Admin guarda un Partido como "Jugado"
@receiver(post_save, sender=Partido)
def actualizar_puntos_al_guardar_resultado(sender, instance, **kwargs):
    if instance.jugado:
        print(f"🔄 Calculando puntos para: {instance}")
        
        # 1. Buscar todos los pronósticos de este partido
        pronosticos = Pronostico.objects.filter(partido=instance)
        
        real_local = instance.goles_local_real
        real_visitante = instance.goles_visitante_real
        
        # 2. Calcular puntos para cada pronóstico
        for pron in pronosticos:
            pred_local = pron.goles_local_prediccion
            pred_visitante = pron.goles_visitante_prediccion
            puntos = 0

            # Si acertó exacto (Ej: Dijo 2-1 y salió 2-1) -> 3 Puntos
            if real_local == pred_local and real_visitante == pred_visitante:
                puntos = 3
            else:
                # Verificamos quién ganó o si fue empate
                gano_local_real = real_local > real_visitante
                gano_visita_real = real_visitante > real_local
                empate_real = real_local == real_visitante
                
                gano_local_pred = pred_local > pred_visitante
                gano_visita_pred = pred_visitante > pred_local
                empate_pred = pred_local == pred_visitante
                
                # Si acertó el resultado (quién ganó) pero no los goles exactos -> 1 Punto
                if (gano_local_real and gano_local_pred) or \
                   (gano_visita_real and gano_visita_pred) or \
                   (empate_real and empate_pred):
                    puntos = 1
            
            # Solo guardamos si cambió el puntaje para optimizar
            if pron.puntos_ganados != puntos:
                pron.puntos_ganados = puntos
                pron.save()

        # 3. ACTUALIZAR EL RANKING (TABLA DE POSICIONES)
        # Recalculamos el total SOLO para los usuarios afectados
        usuarios_afectados = pronosticos.values_list('usuario', flat=True)
        perfiles = PerfilEmpleado.objects.filter(usuario__id__in=usuarios_afectados)

        for perfil in perfiles:
            resultado = Pronostico.objects.filter(usuario=perfil.usuario).aggregate(Sum('puntos_ganados'))
            total = resultado['puntos_ganados__sum']
            perfil.puntos_totales = total if total else 0
            perfil.save()
            
        print("✅ Ranking actualizado automáticamente.")