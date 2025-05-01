from django.core.management.base import BaseCommand
from app_simulador.models import Jugador, Equipo

class Command(BaseCommand):
    help = 'Carga jugadores desde un diccionario, incluyendo información de equipos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Elimina todos los jugadores y equipos antes de cargar'
        )

    def handle(self, *args, **options):
        # Eliminar datos existentes si se especifica --delete
        if options['delete']:
            Jugador.objects.all().delete()
            Equipo.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Datos antiguos eliminados.'))

        # Importar datos
        from app_simulador.data.jugadores_equipos import jugadores

        # Procesar cada equipo
        for equipo_nombre, equipo_data in jugadores.items():
            # Obtener año de fundación (campo obligatorio)
            fundacion = equipo_data.get('fundacion', 1900)  # Valor por defecto
            presupuesto = equipo_data.get('presupuesto', 100_000_000)

            # Crear o obtener equipo
            equipo, creado = Equipo.objects.get_or_create(
                nombre=equipo_nombre,
                defaults={'fundacion': fundacion,'presupuesto': presupuesto }

            )

            if creado:
                self.stdout.write(self.style.SUCCESS(f'✅ Equipo creado: {equipo_nombre}'))
            else:
                self.stdout.write(f'⚠️ Equipo ya existía: {equipo_nombre}')

            # Procesar jugadores por posición
            for clave, valor in equipo_data.items():
                # Ignorar claves que no son posiciones
                if clave not in ['POR', 'DEF', 'MED', 'DEL', 'fundacion']:
                    continue

                if clave == 'fundacion':
                    continue  # Ya procesamos la fundación

                for jugador_data in valor:
                    # Procesar nombre y apellido
                    nombre_completo = jugador_data.get('nombre', '')
                    nombre_partes = nombre_completo.split(' ', 1)
                    nombre = nombre_partes[0]
                    apellido = nombre_partes[1] if len(nombre_partes) > 1 else ''

                    # Crear jugador
                    jugador, creado = Jugador.objects.get_or_create(
                        nombre=nombre,
                        apellido=apellido,
                        equipo=equipo,
                        posicion=clave,
                        defaults={
                            'edad': jugador_data.get('edad', 20),
                            'nacionalidad': jugador_data.get('nacionalidad', 'Desconocida'),
                            'valor_mercado': jugador_data.get('valor_mercado', 5.0),
                            'dorsal': jugador_data.get('dorsal', None),
                            'lesionado': jugador_data.get('lesionado', False),
                            'suspendido': jugador_data.get('suspendido', False)
                        }
                    )

                    if creado:
                        self.stdout.write(self.style.SUCCESS(f'  ✅ Jugador creado: {nombre_completo}'))
                    else:
                        self.stdout.write(f'  ⚠️ Jugador ya existía: {nombre_completo}')

        self.stdout.write(self.style.SUCCESS('\n✅ Carga de datos completada exitosamente!'))