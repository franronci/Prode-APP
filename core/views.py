from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone # Importante para controlar la hora
from django.contrib import messages # Para mostrar errores si el código no existe
from .models import Partido, Pronostico, PerfilEmpleado, Empresa, Torneo

# --- VISTA 1: REGISTRO DE USUARIO ---
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            
            # Buscamos una empresa por defecto para evitar el error
            empresa_default = Empresa.objects.first()
            
            # Si no existe ninguna, creamos una genérica
            if not empresa_default:
                empresa_default = Empresa.objects.create(nombre="Empresa General", codigo_acceso="1234")

            # Creamos el perfil del empleado vinculado a esa empresa
            PerfilEmpleado.objects.create(usuario=usuario, empresa=empresa_default)
            
            # Logueamos al usuario automáticamente
            login(request, usuario)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registro.html', {'form': form})

# --- VISTA 2: HOME ---
def home(request):
    return render(request, 'home.html')

# --- VISTA 3: PRODE (JUEGO) ---
@login_required
def prode(request):
    usuario_actual = request.user
    
    # Hora actual exacta (con zona horaria) para saber si bloqueamos partidos
    ahora = timezone.now()
    
    # 1. Lógica del Dropdown de Fechas
    fechas_disponibles = Partido.objects.values_list('numero_fecha', flat=True).distinct().order_by('numero_fecha')
    
    fecha_seleccionada = request.GET.get('fecha')
    
    # Si no elige fecha, mostramos la primera disponible
    if not fecha_seleccionada and fechas_disponibles:
        fecha_seleccionada = fechas_disponibles.first()
    
    if fecha_seleccionada:
        fecha_seleccionada = int(fecha_seleccionada)

    # 2. Guardado de Pronósticos (POST)
    if request.method == "POST":
        partidos_de_la_fecha = Partido.objects.filter(numero_fecha=fecha_seleccionada)
        
        for partido in partidos_de_la_fecha:
            # SEGURIDAD BACKEND: Solo guardamos si el partido NO ha empezado todavía
            if partido.fecha_hora > ahora:
                goles_local = request.POST.get(f'local_{partido.id}')
                goles_visitante = request.POST.get(f'visitante_{partido.id}')

                if goles_local and goles_visitante:
                    Pronostico.objects.update_or_create(
                        usuario=usuario_actual,
                        partido=partido,
                        defaults={
                            'goles_local_prediccion': int(goles_local),
                            'goles_visitante_prediccion': int(goles_visitante)
                        }
                    )
        return redirect(f'/prode/?fecha={fecha_seleccionada}')

    # 3. Preparar Datos para Mostrar (GET)
    partidos = Partido.objects.filter(numero_fecha=fecha_seleccionada).order_by('fecha_hora')
    
    lista_partidos = []
    
    for p in partidos:
        # Buscamos el pronóstico del usuario para este partido
        pronostico = Pronostico.objects.filter(usuario=usuario_actual, partido=p).first()
        
        # Calculamos si el partido debe mostrarse bloqueado (grisado)
        # Se bloquea si ya tiene resultado (jugado) O si la hora actual ya pasó la hora del partido
        esta_bloqueado = p.jugado or (p.fecha_hora < ahora)

        lista_partidos.append({
            'partido': p,
            'mi_pronostico': pronostico,
            'bloqueado': esta_bloqueado 
        })

    contexto = {
        'lista_partidos': lista_partidos,
        'fechas_disponibles': fechas_disponibles,
        'fecha_seleccionada': fecha_seleccionada,
        'ahora': ahora # Enviamos la hora al template por si acaso
    }

    return render(request, 'prode.html', contexto)

# --- VISTA 4: RANKING ---
def ranking(request):
    # Traemos los perfiles ordenados por puntos (de mayor a menor)
    perfiles = PerfilEmpleado.objects.all().order_by('-puntos_totales')
    return render(request, 'ranking.html', {'perfiles': perfiles})


@login_required
def mis_torneos(request):
    # Crear Torneo
    if request.method == 'POST' and 'crear_torneo' in request.POST:
        nombre = request.POST.get('nombre_torneo')
        if nombre:
            nuevo_torneo = Torneo.objects.create(nombre=nombre, creador=request.user)
            nuevo_torneo.participantes.add(request.user) # El creador se une automático
            return redirect('detalle_torneo', torneo_id=nuevo_torneo.id)

    # Unirse a Torneo
    if request.method == 'POST' and 'unirse_torneo' in request.POST:
        codigo = request.POST.get('codigo_torneo', '').upper().strip()
        try:
            torneo = Torneo.objects.get(codigo=codigo)
            if request.user in torneo.participantes.all():
                messages.warning(request, "¡Ya estás en este torneo!")
            else:
                torneo.participantes.add(request.user)
                messages.success(request, "Te uniste correctamente.")
                return redirect('detalle_torneo', torneo_id=torneo.id)
        except Torneo.DoesNotExist:
            messages.error(request, "Código inválido. Verifica e intenta de nuevo.")

    # Listar mis torneos
    mis_grupos = request.user.torneos_participados.all()
    
    return render(request, 'torneos.html', {'mis_grupos': mis_grupos})

# --- VISTA 6: RANKING DEL TORNEO ---
@login_required
def detalle_torneo(request, torneo_id):
    torneo = Torneo.objects.get(id=torneo_id)
    
    # Seguridad: Solo miembros pueden ver
    if request.user not in torneo.participantes.all():
        return redirect('mis_torneos')

    # Filtramos perfiles SOLO de los participantes de este torneo
    participantes_ids = torneo.participantes.values_list('id', flat=True)
    perfiles = PerfilEmpleado.objects.filter(usuario__id__in=participantes_ids).order_by('-puntos_totales')

    return render(request, 'detalle_torneo.html', {'torneo': torneo, 'perfiles': perfiles})