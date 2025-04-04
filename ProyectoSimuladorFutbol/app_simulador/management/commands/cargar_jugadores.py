from django.core.management.base import BaseCommand
from app_simulador.models import Jugador, Equipo

class Command(BaseCommand):
    help = 'Carga jugadores desde un diccionario'

    def handle(self, *args, **kwargs):
        # Recorremos cada equipo en el diccionario
        from app_simulador.data.jugadores_equipos import jugadores
        for equipo_nombre, equipo_data in jugadores.items():
            equipo, creado = Equipo.objects.get_or_create(nombre=equipo_nombre)

            # Cargar jugadores por posición
            for posicion, jugadores_posicion in equipo_data.items():
                if isinstance(jugadores_posicion, list):
                    for jugador_data in jugadores_posicion:
                        # Si el jugador es un diccionario, extraemos el nombre
                        if isinstance(jugador_data, dict):
                            jugador_nombre = jugador_data.get('nombre', '')
                        else:
                            jugador_nombre = jugador_data
                        nombre, *apellido = jugador_nombre.split(' ')
                        apellido = " ".join(apellido) if apellido else ""

                        # Crear o actualizar el jugador
                        jugador, creado = Jugador.objects.get_or_create(
                            nombre=nombre,
                            apellido=apellido,
                            equipo=equipo,
                            posicion=self.obtener_posicion(posicion),
                            edad=jugador_data.get('edad', 20),
                            nacionalidad=jugador_data.get('nacionalidad', 'Desconocida'),
                            valor_mercado=jugador_data.get('valor_mercado', 5.0),
                            dorsal=None,
                            lesionado=False,
                            suspendido=False,
                        )

                        if creado:
                            self.stdout.write(self.style.SUCCESS(f'Jugador creado: {jugador_nombre}'))
                        else:
                            self.stdout.write(f'Jugador ya existía: {jugador_nombre}')

    def obtener_posicion(self, posicion):
        posiciones = {
            'portero': 'POR',
            'defensas': 'DEF',
            'mediocampistas': 'MED',
            'delanteros': 'DEL'
        }
        return posiciones.get(posicion.lower(), 'DEF')
