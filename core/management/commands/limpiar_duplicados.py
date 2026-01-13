from django.core.management.base import BaseCommand
from core.models import Partido
from django.db.models import Count


class Command(BaseCommand):
    help = 'Elimina partidos duplicados de la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la eliminación sin borrar realmente',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 MODO SIMULACIÓN - No se eliminará nada"))
        
        total_eliminados = 0
        
        # 1. Eliminar duplicados por api_id
        self.stdout.write("\n📋 Buscando duplicados por api_id...")
        duplicados_api = Partido.objects.values('api_id').annotate(
            count=Count('api_id')
        ).filter(count__gt=1, api_id__isnull=False)
        
        self.stdout.write(f"Encontrados {duplicados_api.count()} grupos de duplicados por api_id")
        
        for dup in duplicados_api:
            api_id = dup['api_id']
            partidos = Partido.objects.filter(api_id=api_id).order_by('id')
            
            mantener = partidos.first()
            eliminar = partidos[1:]
            
            self.stdout.write(f"\n  api_id '{api_id}':")
            self.stdout.write(f"    ✅ Manteniendo: ID {mantener.id} - {mantener}")
            for p in eliminar:
                self.stdout.write(f"    ❌ Eliminando: ID {p.id} - {p}")
                if not dry_run:
                    p.delete()
                total_eliminados += 1
        
        # 2. Eliminar duplicados por equipo_local, equipo_visitante y numero_fecha (para partidos sin api_id)
        self.stdout.write("\n📋 Buscando duplicados por equipos y fecha (sin api_id)...")
        duplicados_equipos = Partido.objects.values(
            'equipo_local', 'equipo_visitante', 'numero_fecha'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        self.stdout.write(f"Encontrados {duplicados_equipos.count()} grupos de duplicados por equipos/fecha")
        
        for dup in duplicados_equipos:
            partidos = Partido.objects.filter(
                equipo_local=dup['equipo_local'],
                equipo_visitante=dup['equipo_visitante'],
                numero_fecha=dup['numero_fecha']
            ).order_by('id')
            
            # Si todos tienen api_id=None, eliminar duplicados
            if partidos.filter(api_id__isnull=True).count() == partidos.count():
                mantener = partidos.first()
                eliminar = partidos[1:]
                
                self.stdout.write(f"\n  {dup['equipo_local']} vs {dup['equipo_visitante']} (Fecha {dup['numero_fecha']}):")
                self.stdout.write(f"    ✅ Manteniendo: ID {mantener.id} - {mantener}")
                for p in eliminar:
                    self.stdout.write(f"    ❌ Eliminando: ID {p.id} - {p}")
                    if not dry_run:
                        p.delete()
                    total_eliminados += 1
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"\n🔍 SIMULACIÓN: Se eliminarían {total_eliminados} partidos duplicados"
            ))
            self.stdout.write("   Ejecuta sin --dry-run para eliminar realmente")
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Total de partidos duplicados eliminados: {total_eliminados}"
            ))
