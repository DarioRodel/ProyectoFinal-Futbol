from django.core.management.base import BaseCommand
from app_simulador.models import Logro

class Command(BaseCommand):
    help = 'Crea los logros iniciales en la base de datos'

    def handle(self, *args, **kwargs):
        # Lista de logros que se van a insertar
        logros = [
            {"nombre": "Primer Equipo", "descripcion": "Has escogido tu primer equipo.", "icono": "users"},
            {"nombre": "Primer Partido", "descripcion": "Has simulado tu primer partido.", "icono": "futbol"},
            {"nombre": "Líder de la Liga", "descripcion": "Has alcanzado el primer lugar en la tabla de la liga.",
             "icono": "trophy"},
            {"nombre": "10 Victorias", "descripcion": "Has ganado 10 partidos.", "icono": "medal"},
            {"nombre": "Campeón de la Liga", "descripcion": "Has ganado la liga.", "icono": "star"},
            {"nombre": "Temporada Completa", "descripcion": "Has finalizado la temporada.", "icono": "flag-checkered"},
        ]

        # Iteramos sobre cada logro y lo creamos si no existe aún
        for logro_data in logros:
            Logro.objects.get_or_create(**logro_data)

        self.stdout.write(self.style.SUCCESS('Logros creados exitosamente.'))
