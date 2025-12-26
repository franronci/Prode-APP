from django.db import models
from django.contrib.auth.models import User
import uuid # <--- Agregar import al principio del archivo

# 1. Modelo de EMPRESA (Tus clientes)
class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_acceso = models.CharField(max_length=20, unique=True, help_text="Código para que los empleados se registren")

    def __str__(self):
        return self.nombre

# 2. Perfil de USUARIO (Extensión del empleado)
# Django ya trae un usuario básico, aquí le agregamos la relación con la empresa
class PerfilEmpleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    # --- CAMBIO AQUÍ ---
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    # -------------------
    puntos_totales = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.usuario.username} - {self.empresa.nombre if self.empresa else 'Sin Empresa'}"

# 3. Modelo de PARTIDO (El fixture del mundial)
class Partido(models.Model):
    api_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    numero_fecha = models.IntegerField(default=1) 
    
    equipo_local = models.CharField(max_length=50)
    # --- NUEVO CAMPO ---
    escudo_local = models.URLField(max_length=200, null=True, blank=True)
    
    equipo_visitante = models.CharField(max_length=50)
    # --- NUEVO CAMPO ---
    escudo_visitante = models.URLField(max_length=200, null=True, blank=True)
    
    fecha_hora = models.DateTimeField()
    goles_local_real = models.IntegerField(null=True, blank=True)
    goles_visitante_real = models.IntegerField(null=True, blank=True)
    jugado = models.BooleanField(default=False)

    def __str__(self):
        return f"F{self.numero_fecha}: {self.equipo_local} vs {self.equipo_visitante}"

# 4. Modelo de PRONÓSTICO (La apuesta del usuario)
class Pronostico(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    
    goles_local_prediccion = models.IntegerField()
    goles_visitante_prediccion = models.IntegerField()
    
    puntos_ganados = models.IntegerField(default=0)

    class Meta:
        unique_together = ('usuario', 'partido')

    def __str__(self):
        return f"{self.usuario} - {self.partido}"

    # --- AQUÍ ESTÁ LA LÓGICA DE PUNTOS ---
    def actualizar_puntos(self):
        # Si el partido no se jugó, no hacemos nada
        if not self.partido.jugado:
            return

        # Resultados reales
        real_local = self.partido.goles_local_real
        real_visitante = self.partido.goles_visitante_real
        
        # Predicciones
        pred_local = self.goles_local_prediccion
        pred_visitante = self.goles_visitante_prediccion

        # 1. ¿Acertó el resultado exacto? (Ej: Dijo 2-1 y salió 2-1)
        if real_local == pred_local and real_visitante == pred_visitante:
            self.puntos_ganados = 3
        
        # 2. ¿Acertó quién ganaba (o el empate), aunque no los goles exactos?
        # Checkeamos si el signo es el mismo (Ambos ganan local, o ambos empate, o ambos visitante)
        elif (real_local > real_visitante and pred_local > pred_visitante) or \
             (real_local == real_visitante and pred_local == pred_visitante) or \
             (real_local < real_visitante and pred_local < pred_visitante):
            self.puntos_ganados = 1
        
        # 3. No acertó nada
        else:
            self.puntos_ganados = 0
            
        # Guardamos el cambio en la base de datos
        self.save()
        
        # EXTRA: Actualizar también los puntos totales del empleado
        self.actualizar_perfil_empleado()

    def actualizar_perfil_empleado(self):
        # Buscamos el perfil del empleado y le recalculamos el total
        # (Esto suma TODOS sus pronósticos de nuevo para estar seguros)
        perfil = self.usuario.perfilempleado
        total = 0
        pronosticos_usuario = Pronostico.objects.filter(usuario=self.usuario)
        for p in pronosticos_usuario:
            total += p.puntos_ganados
        
        perfil.puntos_totales = total
        perfil.save()

    class Meta:
        unique_together = ('usuario', 'partido') # Un usuario solo puede pronosticar una vez por partido


class Torneo(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True, editable=False)
    # Relación muchos a muchos: Un usuario puede estar en muchos torneos
    participantes = models.ManyToManyField(User, related_name='torneos_participados')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='torneos_creados')

    def save(self, *args, **kwargs):
        # Generamos código único automático si no tiene
        if not self.codigo:
            self.codigo = str(uuid.uuid4()).replace('-', '')[:6].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"