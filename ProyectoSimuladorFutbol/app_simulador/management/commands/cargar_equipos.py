from django.core.management.base import BaseCommand
from app_simulador.models import Equipo


# Comando personalizado para cargar equipos de La Liga con datos reales
class Command(BaseCommand):
    help = 'Carga los equipos de La Liga con datos reales'

    def handle(self, *args, **options):
        # Definimos una lista con los datos de los equipos que vamos a cargar en la base de datos
        equipos = [
            {
                'nombre': 'Real Madrid',
                'ciudad': 'Madrid',
                'estadio': 'Santiago Bernabéu',
                'fundacion': 1902,
                'presupuesto': 800000000,
                'equipacion_principal': 'Blanco',
                'equipacion_alternativa': 'Negro'
            },
            {
                'nombre': 'FC Barcelona',
                'ciudad': 'Barcelona',
                'estadio': 'Spotify Camp Nou',
                'fundacion': 1899,
                'presupuesto': 800000000,
                'equipacion_principal': 'Azulgrana',
                'equipacion_alternativa': 'Dorado'
            },
            {
                'nombre': 'Atlético de Madrid',
                'ciudad': 'Madrid',
                'estadio': 'Cívitas Metropolitano',
                'fundacion': 1903,
                'presupuesto': 400000000,
                'equipacion_principal': 'Rojiblanco',
                'equipacion_alternativa': 'Azul marino'
            },
            {
                'nombre': 'Sevilla FC',
                'ciudad': 'Sevilla',
                'estadio': 'Ramón Sánchez-Pizjuán',
                'fundacion': 1890,
                'presupuesto': 250000000,
                'equipacion_principal': 'Blanco',
                'equipacion_alternativa': 'Rojo'
            },
            {
                'nombre': 'Real Sociedad',
                'ciudad': 'San Sebastián',
                'estadio': 'Reale Arena',
                'fundacion': 1909,
                'presupuesto': 200000000,
                'equipacion_principal': 'Blanco y azul',
                'equipacion_alternativa': 'Negro'
            },
            {
                'nombre': 'Villarreal CF',
                'ciudad': 'Villarreal',
                'estadio': 'Estadio de la Cerámica',
                'fundacion': 1923,
                'presupuesto': 180000000,
                'equipacion_principal': 'Amarillo',
                'equipacion_alternativa': 'Azul'
            },
            {
                'nombre': 'Real Betis',
                'ciudad': 'Sevilla',
                'estadio': 'Benito Villamarín',
                'fundacion': 1907,
                'presupuesto': 150000000,
                'equipacion_principal': 'Verde y blanco',
                'equipacion_alternativa': 'Negro'
            },
            {
                'nombre': 'Athletic Club',
                'ciudad': 'Bilbao',
                'estadio': 'San Mamés',
                'fundacion': 1898,
                'presupuesto': 120000000,
                'equipacion_principal': 'Rojo y blanco',
                'equipacion_alternativa': 'Negro'
            },
            {
                'nombre': 'Valencia CF',
                'ciudad': 'Valencia',
                'estadio': 'Mestalla',
                'fundacion': 1919,
                'presupuesto': 150000000,
                'equipacion_principal': 'Blanco',
                'equipacion_alternativa': 'Naranja'
            },
            {
                'nombre': 'Celta de Vigo',
                'ciudad': 'Vigo',
                'estadio': 'Abanca-Balaídos',
                'fundacion': 1923,
                'presupuesto': 80000000,
                'equipacion_principal': 'Celeste',
                'equipacion_alternativa': 'Blanco'
            },
            {
                'nombre': 'Getafe CF',
                'ciudad': 'Getafe',
                'estadio': 'Coliseum Alfonso Pérez',
                'fundacion': 1983,
                'presupuesto': 60000000,
                'equipacion_principal': 'Azul',
                'equipacion_alternativa': 'Blanco'
            },
            {
                'nombre': 'CA Osasuna',
                'ciudad': 'Pamplona',
                'estadio': 'El Sadar',
                'fundacion': 1920,
                'presupuesto': 60000000,
                'equipacion_principal': 'Rojo',
                'equipacion_alternativa': 'Azul'
            },
            {
                'nombre': 'Rayo Vallecano',
                'ciudad': 'Madrid',
                'estadio': 'Vallecas',
                'fundacion': 1924,
                'presupuesto': 50000000,
                'equipacion_principal': 'Blanco',
                'equipacion_alternativa': 'Rojo'
            },
            {
                'nombre': 'RCD Mallorca',
                'ciudad': 'Palma de Mallorca',
                'estadio': 'Visit Mallorca Estadi',
                'fundacion': 1916,
                'presupuesto': 50000000,
                'equipacion_principal': 'Rojo y negro',
                'equipacion_alternativa': 'Blanco'
            },
            {
                'nombre': 'Girona FC',
                'ciudad': 'Girona',
                'estadio': 'Montilivi',
                'fundacion': 1930,
                'presupuesto': 50000000,
                'equipacion_principal': 'Blanco y rojo',
                'equipacion_alternativa': 'Azul'
            },
            {
                'nombre': 'Real Valladolid',
                'ciudad': 'Valladolid',
                'estadio': 'José Zorrilla',
                'fundacion': 1928,
                'presupuesto': 50000000,
                'equipacion_principal': 'Blanco y violeta',
                'equipacion_alternativa': 'Negro'
            },
            {
                'nombre': 'CD Leganés',
                'ciudad': 'Leganés',
                'estadio': 'Butarque',
                'fundacion': 1928,
                'presupuesto': 40000000,
                'equipacion_principal': 'Blanco y azul',
                'equipacion_alternativa': 'Negro'
            },
            {
                'nombre': 'RCD Espanyol',
                'ciudad': 'Barcelona',
                'estadio': 'RCDE Stadium',
                'fundacion': 1900,
                'presupuesto': 70000000,
                'equipacion_principal': 'Blanco y azul',
                'equipacion_alternativa': 'Amarillo'
            },
            {
                'nombre': 'UD Las Palmas',
                'ciudad': 'Las Palmas',
                'estadio': 'Gran Canaria',
                'fundacion': 1949,
                'presupuesto': 40000000,
                'equipacion_principal': 'Amarillo y azul',
                'equipacion_alternativa': 'Blanco'
            },
            {
                'nombre': 'Deportivo Alavés',
                'ciudad': 'Vitoria',
                'estadio': 'Mendizorroza',
                'fundacion': 1921,
                'presupuesto': 50000000,
                'equipacion_principal': 'Azul y blanco',
                'equipacion_alternativa': 'Rojo'
            }
        ]

        # Iteramos por cada diccionario de equipo
        for datos in equipos:
            # Usamos update_or_create para evitar duplicados:
            # Si el equipo ya existe (por nombre), lo actualiza. Si no, lo crea.
            Equipo.objects.update_or_create(
                nombre=datos['nombre'],  # Condición para buscar el equipo
                defaults=datos  # Si se encuentra, se actualiza con estos valores; si no, se usa para crear uno nuevo
            )

        # Mostramos un mensaje por consola indicando que todo fue exitoso
        self.stdout.write(self.style.SUCCESS('Equipos cargados exitosamente!'))
