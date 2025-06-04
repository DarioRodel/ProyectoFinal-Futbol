from django.core.management.base import BaseCommand
from app_simulador.models import Equipo


class Command(BaseCommand):
    help = 'Genera calendario round-robin para 20 equipos (38 jornadas)'

    def handle(self, *args, **options):
        equipos = list(Equipo.objects.all().order_by('id'))

        if len(equipos) != 20:
            self.stdout.write(self.style.ERROR('Debe haber exactamente 20 equipos'))
            return

        # Generar calendario usando algoritmo round-robin
        calendario_completo = self.generar_round_robin_mejorado(equipos)

        # Asignar calendario a cada equipo
        for equipo in equipos:
            calendario_equipo = []
            for jornada in calendario_completo:
                for partido in jornada:
                    if partido[0] == equipo:
                        calendario_equipo.append(partido[1].id)
                    elif partido[1] == equipo:
                        calendario_equipo.append(partido[0].id)
            equipo.calendario = calendario_equipo
            equipo.save()

        self.stdout.write(self.style.SUCCESS('Calendario generado correctamente'))

    def generar_round_robin_mejorado(self, equipos):
        n = len(equipos)
        mitad = n // 2
        calendario = []
        equipos_rotantes = equipos[1:]  # Excluir el primer equipo

        for _ in range(n - 1):
            jornada = []
            jornada.append((equipos[0], equipos_rotantes[-1]))

            # Emparejar el resto
            for i in range(mitad - 1):
                jornada.append((equipos_rotantes[i], equipos_rotantes[-i - 2]))

            calendario.append(jornada)

            # Rotar los equipos
            equipos_rotantes = [equipos_rotantes[-1]] + equipos_rotantes[:-1]

        # Generar segunda vuelta invirtiendo localías
        segunda_vuelta = []
        for jornada in calendario:
            nueva_jornada = [(visitante, local) for local, visitante in jornada]
            segunda_vuelta.append(nueva_jornada)

        return calendario + segunda_vuelta