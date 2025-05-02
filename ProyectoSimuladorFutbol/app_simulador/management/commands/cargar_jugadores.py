from django.core.management.base import BaseCommand
from app_simulador.models import Jugador, Equipo
# Importamos el diccionario de datos desde un archivo
from app_simulador.data.jugadores_equipos import jugadores


# Comando personalizado para cargar jugadores y equipos desde un diccionario
class Command(BaseCommand):
    help = 'Carga jugadores desde un diccionario, incluyendo información de equipos'

    def add_arguments(self, parser):
        # Agregamos una opción al comando: --delete, que elimina los datos antes de cargar
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Elimina todos los jugadores y equipos antes de cargar'
        )

    def handle(self, *args, **options):
        # Si se usa la opción --delete, eliminamos todos los registros de Jugador y Equipo
        if options['delete']:
            Jugador.objects.all().delete()
            Equipo.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Datos antiguos eliminados.'))

        # Iteramos sobre cada equipo del diccionario
        for equipo_nombre, equipo_data in jugadores.items():
            # Obtenemos datos básicos del equipo con valores por defecto si faltan
            fundacion = equipo_data.get('fundacion', 1900)
            presupuesto = equipo_data.get('presupuesto', 100_000_000)

            # Creamos el equipo si no existe, o lo obtenemos si ya está creado
            equipo, creado = Equipo.objects.get_or_create(
                nombre=equipo_nombre,
                defaults={
                    'fundacion': fundacion,
                    'presupuesto': presupuesto
                }
            )

            # Informamos si se creó el equipo o si ya existía
            if creado:
                self.stdout.write(self.style.SUCCESS(f'✅ Equipo creado: {equipo_nombre}'))
            else:
                self.stdout.write(f'⚠️ Equipo ya existía: {equipo_nombre}')

            # Iteramos sobre las claves del diccionario para encontrar posiciones de jugadores
            for clave, valor in equipo_data.items():
                # Ignoramos claves que no son posiciones (ni fundación)
                if clave not in ['POR', 'DEF', 'MED', 'DEL']:
                    continue

                # Iteramos sobre los jugadores de esa posición
                for jugador_data in valor:
                    # Procesamos el nombre completo separándolo en nombre y apellido
                    nombre_completo = jugador_data.get('nombre', '')
                    nombre_partes = nombre_completo.split(' ', 1)
                    nombre = nombre_partes[0]
                    apellido = nombre_partes[1] if len(nombre_partes) > 1 else ''

                    # Creamos o buscamos al jugador, y usamos valores por defecto si falta información
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

                    # Mostramos en consola si se creó o ya existía
                    if creado:
                        self.stdout.write(self.style.SUCCESS(f'  ✅ Jugador creado: {nombre_completo}'))
                    else:
                        self.stdout.write(f'  ⚠️ Jugador ya existía: {nombre_completo}')

        # Mensaje final cuando todo se ha procesado correctamente
        self.stdout.write(self.style.SUCCESS('\n✅ Carga de datos completada exitosamente!'))
