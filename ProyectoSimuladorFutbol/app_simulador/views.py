import json
import logging
from django.templatetags.static import static
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.views.generic import ListView, DetailView
from .models import Equipo, UserProfile, UsuarioLogro, Jugador, Partido
from .forms import CustomUserCreationForm
import random
from app_simulador.data.jugadores_equipos import jugadores as jugadores_equipos
from .utils import otorgar_logro


# Vista para la página de inicio
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


# Vista para la página de inicio de sesión
class InicioView(View):
    def get(self, request):
        # Redirigir al menú si ya está autenticado y tiene equipo
        if request.user.is_authenticated:
            perfil = getattr(request.user, 'userprofile', None)
            if perfil and perfil.equipo_seleccionado:
                return redirect('menu')
        return render(request, 'inicio.html')


# Vista para el registro de usuarios
class RegistroView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registro.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                UserProfile.objects.create(user=user)
                login(request, user)
            return redirect('menu')
        return render(request, 'registro.html', {'form': form})


# Vista para el inicio de sesión
class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('menu')
        return render(request, 'login.html', {'form': form})


# Vista para cerrar sesión
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


# Vista para seleccionar un equipo
class SeleccionarEquipoView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile

        # Redirigir al menú si ya tiene equipo
        if perfil.equipo_seleccionado:
            return redirect('menu')

        equipos = Equipo.objects.all()
        imagenes_escudos = {
            "Deportivo Alavés": "images/escudos/alaves.png",
            "Athletic Club": "images/escudos/bilbao.png",
            "Atlético de Madrid": "images/escudos/atletico.png",
            "Barcelona": "images/escudos/barca.png",
            "Real Betis": "images/escudos/betis.png",
            "Celta de Vigo": "images/escudos/celta.png",
            "Getafe CF": "images/escudos/getafe.png",
            "Girona FC": "images/escudos/girona.png",
            "UD Las Palmas": "images/escudos/palmas.png",
            "RCD Mallorca": "images/escudos/mallorca.png",
            "CA Osasuna": "images/escudos/osasuna.png",
            "CD Leganés": "images/escudos/leganes.png",
            "Rayo Vallecano": "images/escudos/rayo.png",
            "Real Madrid": "images/escudos/realmadrid.png",
            "Real Sociedad": "images/escudos/realsociedad.png",
            "Sevilla FC": "images/escudos/sevilla.png",
            "Real Valladolid": "images/escudos/valladolid.png",
            "Valencia CF": "images/escudos/valencia.png",
            "RCD Espanyol": "images/escudos/espanyol.png",
            "Villarreal CF": "images/escudos/villareal.png",
        }

        for equipo in equipos:
            equipo.ruta_escudo = imagenes_escudos.get(equipo.nombre, "images/escudos/barca.png")

        return render(request, 'seleccion_equipo.html', {
            'equipos': equipos,
            'tiene_equipo': False
        })


# Vista para asignar un equipo
class AsignarEquipoView(LoginRequiredMixin, View):
    def get(self, request, equipo_id):
        equipo = get_object_or_404(Equipo, id=equipo_id)
        perfil = request.user.userprofile

        # Verificar si ya tiene equipo
        if perfil.equipo_seleccionado:
            return render(request, 'confirmar_cambio_equipo.html', {
                'equipo_actual': perfil.equipo_seleccionado,
                'nuevo_equipo': equipo
            })

        # Asignar nuevo equipo
        with transaction.atomic():
            perfil.equipo_seleccionado = equipo
            perfil.save()
            otorgar_logro(request.user, "Primer Equipo")

        return redirect('menu')


# Vista para confirmar cambio de equipo
class ConfirmarCambioEquipoView(LoginRequiredMixin, View):
    def post(self, request, equipo_id):
        equipo = get_object_or_404(Equipo, id=equipo_id)
        perfil = request.user.userprofile

        with transaction.atomic():
            # Resetear estadísticas del equipo actual
            if perfil.equipo_seleccionado:
                equipo_actual = perfil.equipo_seleccionado
                equipo_actual.puntos = 0
                equipo_actual.partidos_jugados = 0
                equipo_actual.partidos_ganados = 0
                equipo_actual.partidos_perdidos = 0
                equipo_actual.partidos_empatados = 0
                equipo_actual.temporada_finalizada = False
                equipo_actual.save()

            # Asignar nuevo equipo
            perfil.equipo_seleccionado = equipo
            perfil.save()

        return redirect('menu')


# Vista para el menú principal
class MenuView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile

        # Redirigir si no hay equipo seleccionado
        if not perfil.equipo_seleccionado:
            return redirect('seleccionar_equipo')

        equipos = Equipo.objects.order_by('-puntos')

        # Verificar si el usuario es líder
        if perfil.equipo_seleccionado == equipos.first():
            otorgar_logro(request.user, "Líder de la Liga")

        return render(request, 'menu.html', {
            'equipos': equipos,
            'equipo_asignado': perfil.equipo_seleccionado
        })


# Vista para eliminar temporada
class EliminarTemporadaView(LoginRequiredMixin, View):
    def post(self, request):
        # Resetear las estadísticas de todos los equipos
        equipos = Equipo.objects.all()
        for equipo in equipos:
            equipo.puntos = 0
            equipo.partidos_jugados = 0
            equipo.partidos_ganados = 0
            equipo.partidos_perdidos = 0
            equipo.partidos_empatados = 0
            equipo.temporada_finalizada = False
            equipo.ya_jugo = False
            equipo.save()

        # Eliminar equipo seleccionado en el perfil del usuario
        perfil = request.user.userprofile
        perfil.equipo_seleccionado = None
        perfil.save()

        return redirect('seleccionar_equipo')

class FormacionEquipoView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile
        equipo = perfil.equipo_seleccionado

        if not equipo:
            return redirect('seleccionar_equipo')

        # Obtener jugadores del diccionario importado correctamente
        jugadores = jugadores_equipos.get(equipo.nombre, {})

        # Organizar jugadores por posición según la formación seleccionada
        jugadores_por_posicion = {
            'portero': jugadores.get('PORTERO', [])[0] if jugadores.get('PORTERO') else 'Sin portero',
            'defensas': jugadores.get('DEFENSA', []),
            'mediocampistas': jugadores.get('MEDIOCAMPISTA', []),
            'delanteros': jugadores.get('DELANTERO', [])
        }

        formacion_actual = getattr(perfil, 'formacion', '4-4-2') or '4-4-2'

        return render(request, 'formacion_equipo.html', {
            'equipo': equipo,
            'jugadores_por_posicion': jugadores_por_posicion,
            'formacion_actual': formacion_actual
        })

class GuardarFormacionView(LoginRequiredMixin, View):
    def post(self, request):
        perfil = request.user.userprofile
        formacion = request.POST.get('formacion')

        if formacion in ['4-4-2', '4-3-3', '3-5-2', '4-2-3-1']:
            perfil.formacion = formacion
            perfil.save()
            request.session['formacion_mensaje'] = f"Formación cambiada a {formacion}"
        else:
            request.session['formacion_mensaje'] = "Formación no válida"

        return redirect('formacion_equipo')

# Vista para notificaciones
class NotificacionesView(LoginRequiredMixin, View):
    def get(self, request):
        logros = UsuarioLogro.objects.filter(usuario=request.user).order_by('-fecha_obtenido')
        return render(request, 'notificaciones.html', {
            'logros_obtenidos': logros,
            'mostrar_popup': False
        })

# Vista para tabla de liga
class TablaLigaView(LoginRequiredMixin, View):
    def get(self, request):
        equipos = Equipo.objects.order_by('-puntos')
        perfil = request.user.userprofile
        equipo_asignado = perfil.equipo_seleccionado

        # Verificar si el equipo del usuario está en primer lugar
        if equipo_asignado and equipos.first() == equipo_asignado:
            otorgar_logro(request.user, "Líder de la Liga")

        # Agregar escudos
        imagenes_escudos = {
            "Deportivo Alavés": "images/escudos/alaves.png",
            "Athletic Club": "images/escudos/bilbao.png",
            "Atlético de Madrid": "images/escudos/atletico.png",
            "Barcelona": "images/escudos/barca.png",
            "Real Betis": "images/escudos/betis.png",
            "Celta de Vigo": "images/escudos/celta.png",
            "Getafe CF": "images/escudos/getafe.png",
            "Girona FC": "images/escudos/girona.png",
            "UD Las Palmas": "images/escudos/palmas.png",
            "RCD Mallorca": "images/escudos/mallorca.png",
            "CA Osasuna": "images/escudos/osasuna.png",
            "CD Leganés": "images/escudos/leganes.png",
            "Rayo Vallecano": "images/escudos/rayo.png",
            "Real Madrid": "images/escudos/realmadrid.png",
            "Real Sociedad": "images/escudos/realsociedad.png",
            "Sevilla FC": "images/escudos/sevilla.png",
            "Real Valladolid": "images/escudos/valladolid.png",
            "Valencia CF": "images/escudos/valencia.png",
            "RCD Espanyol": "images/escudos/espanyol.png",
            "Villarreal CF": "images/escudos/villareal.png",
        }

        for equipo in equipos:
            equipo.ruta_escudo = imagenes_escudos.get(equipo.nombre, "images/escudos/barca.png")

        response = render(request, 'tabla_liga.html', {
            'equipos': equipos,
            'equipo_asignado': equipo_asignado
        })
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


# Vista para finalizar temporada
class FinalizarTemporadaView(LoginRequiredMixin, View):
    def get(self, request):
        # Obtener el perfil del usuario y su equipo
        perfil = request.user.userprofile
        equipo_asignado = perfil.equipo_seleccionado

        # Verificar si el usuario tiene equipo asignado
        if not equipo_asignado:
            return redirect('seleccionar_equipo')

        # Marcar la temporada como finalizada
        equipo_asignado.temporada_finalizada = True
        equipo_asignado.save()

        otorgar_logro(request.user, "Temporada Completa")

        equipos_ordenados = Equipo.objects.order_by('-puntos')
        if equipos_ordenados.first() == equipo_asignado:
            otorgar_logro(request.user, "Campeón de la Liga")

        return redirect('menu')


class InformacionEquipoView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile
        equipo = perfil.equipo_seleccionado

        if not equipo:
            return redirect('seleccionar_equipo')

        # Obtener escudo del equipo
        imagenes_escudos = {
            "Deportivo Alavés": "images/escudos/alaves.png",
            "Athletic Club": "images/escudos/bilbao.png",
            "Atlético de Madrid": "images/escudos/atletico.png",
            "Barcelona": "images/escudos/barca.png",
            "Real Betis": "images/escudos/betis.png",
            "Celta de Vigo": "images/escudos/celta.png",
            "Getafe CF": "images/escudos/getafe.png",
            "Girona FC": "images/escudos/girona.png",
            "UD Las Palmas": "images/escudos/palmas.png",
            "RCD Mallorca": "images/escudos/mallorca.png",
            "CA Osasuna": "images/escudos/osasuna.png",
            "CD Leganés": "images/escudos/leganes.png",
            "Rayo Vallecano": "images/escudos/rayo.png",
            "Real Madrid": "images/escudos/realmadrid.png",
            "Real Sociedad": "images/escudos/realsociedad.png",
            "Sevilla FC": "images/escudos/sevilla.png",
            "Real Valladolid": "images/escudos/valladolid.png",
            "Valencia CF": "images/escudos/valencia.png",
            "RCD Espanyol": "images/escudos/espanyol.png",
            "Villarreal CF": "images/escudos/villareal.png",
        }
        ruta_escudo = imagenes_escudos.get(equipo.nombre, "images/escudos/default.png")

        return render(request, 'informacion_equipo.html', {
            'equipo': equipo,
            'ruta_escudo': ruta_escudo
        })


class JugadoresEquipoView(LoginRequiredMixin, ListView):
    model = Jugador
    template_name = 'jugadores_equipo.html'
    context_object_name = 'jugadores'

    def get_queryset(self):
        perfil = self.request.user.userprofile
        equipo = perfil.equipo_seleccionado
        return Jugador.objects.filter(equipo=equipo).order_by('posicion', 'dorsal')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jugadores = self.get_queryset()

        # Separar jugadores por posición base
        porteros = list(jugadores.filter(posicion='POR'))
        defensas_raw = list(jugadores.filter(posicion='DEF'))
        mediocampistas_raw = list(jugadores.filter(posicion='MED'))
        delanteros_raw = list(jugadores.filter(posicion='DEL'))

        # 1. Mover defensas excedentes a mediocampistas
        defensas_final = defensas_raw[:5]
        mediocampistas_temp = mediocampistas_raw + defensas_raw[5:]  # Combinar con originales

        # 2. Mover mediocampistas excedentes a delanteros
        mediocampistas_final = mediocampistas_temp[:5]
        delanteros_final = delanteros_raw + mediocampistas_temp[5:]  # Combinar con originales

        context.update({
            'equipo': self.request.user.userprofile.equipo_seleccionado,
            'porteros': porteros,
            'defensas': defensas_final,
            'mediocampistas': mediocampistas_final,
            'delanteros': delanteros_final
        })

        return context

class DetalleJugadorView(LoginRequiredMixin, DetailView):
    model = Jugador
    template_name = 'detalle_jugador.html'
    context_object_name = 'jugador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipo'] = self.request.user.userprofile.equipo_seleccionado
        return context
# Vista para simular partido

logger = logging.getLogger(__name__)
class SimularPartidoView(LoginRequiredMixin, View):
    template_name = 'simular_partido.html'
    ESCUDOS_MAP = {
        "Deportivo Alavés": "alaves.png",
        "Athletic Club": "bilbao.png",
        "Atlético de Madrid": "atletico.png",
        "FC Barcelona": "barca.png",
        "Real Betis": "betis.png",
        "Celta de Vigo": "celta.png",
        "Getafe CF": "getafe.png",
        "Girona FC": "girona.png",
        "UD Las Palmas": "palmas.png",
        "RCD Mallorca": "mallorca.png",
        "CA Osasuna": "osasuna.png",
        "CD Leganés": "leganes.png",
        "Rayo Vallecano": "rayo.png",
        "Real Madrid": "realmadrid.png",
        "Real Sociedad": "realsociedad.png",
        "Sevilla FC": "sevilla.png",
        "Real Valladolid": "valladolid.png",
        "Valencia CF": "valencia.png",
        "RCD Espanyol": "espanyol.png",
        "Villarreal CF": "villareal.png",
    }

    def get(self, request):
        try:
            perfil = request.user.userprofile
            equipo = perfil.equipo_seleccionado

            # Obtener jornada actual desde el perfil del usuario o sesión
            jornada_actual = perfil.jornada_actual if hasattr(perfil, 'jornada_actual') else 1

            # Asegurarse de que la jornada no sea menor que 1
            if jornada_actual < 1:
                perfil.jornada_actual = 1
                perfil.save()

            # Si no ha llegado al final de la temporada, seleccionar un oponente
            oponente = self.seleccionar_oponente(equipo)

            request.session['oponente_id'] = oponente.id

            contexto = {
                'equipo_usuario': equipo,
                'escudo_usuario': self.obtener_ruta_escudo(equipo),
                'oponente': oponente,
                'escudo_oponente': self.obtener_ruta_escudo(oponente),
                'eventos_json': json.dumps([]),
                'partido': {'estadisticas': self.estadisticas_base()},
                'jornada_actual': jornada_actual
            }

            return render(request, self.template_name, contexto)
        except Exception as e:
            logger.error(f"Error en GET: {str(e)}")
            return render(request, 'error.html', {'error': str(e)})

    def post(self, request):
        try:
            perfil = request.user.userprofile
            equipo_usuario = perfil.equipo_seleccionado
            oponente_id = request.session.get('oponente_id')

            # Obtener jornada actual
            jornada_actual = perfil.jornada_actual if hasattr(perfil, 'jornada_actual') else 1

            # Asegurarse de que la jornada no sea menor que 1
            if jornada_actual < 1:
                perfil.jornada_actual = 1
                perfil.save()


            if not oponente_id:
                return JsonResponse({'status': 'error', 'message': 'No se encontró el oponente'}, status=400)

            oponente = Equipo.objects.get(id=oponente_id)

            # Calcular fuerza y goles
            fuerza_local = self.calcular_fuerza(equipo_usuario, perfil.formacion)
            fuerza_visitante = self.calcular_fuerza(oponente, '4-4-2')
            goles_local = self.generar_goles(fuerza_local, fuerza_visitante)
            goles_visitante = self.generar_goles(fuerza_visitante, fuerza_local)

            # Simular eventos
            eventos_data = self.simular_eventos(goles_local, goles_visitante)

            # Crear partido
            Partido.objects.create(
                equipo_local=equipo_usuario,
                equipo_visitante=oponente,
                goles_local=goles_local,
                goles_visitante=goles_visitante,
                eventos=eventos_data['eventos'],
                estadisticas=eventos_data['estadisticas_final'],
                estado='finalizado'
            )

            self.actualizar_estadisticas_equipos(equipo_usuario, oponente, goles_local, goles_visitante)

            oponente.ya_jugo = True
            oponente.save()

            # Actualizar la jornada en el perfil del usuario
            perfil.jornada_actual = jornada_actual + 1
            perfil.save()

            request.session.pop('oponente_id', None)

            return JsonResponse({
                'status': 'success',
                'oponente': {
                    'nombre': oponente.nombre,
                    'escudo': self.obtener_ruta_escudo(oponente)
                },
                'goles_usuario': goles_local,
                'goles_oponente': goles_visitante,
                'eventos': eventos_data['eventos'],
                'estadisticas': eventos_data['estadisticas_minuto_a_minuto'],
                'resultado': self.definir_resultado(goles_local, goles_visitante),
                'jornada_actual': jornada_actual + 1
            }, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            logger.error(f"Error en POST: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error interno del servidor'}, status=500)

    def obtener_ruta_escudo(self, equipo):
        if not equipo:
            return static('images/escudos/realmadrid.png')
        nombre_archivo = self.ESCUDOS_MAP.get(equipo.nombre, 'realmadrid.png')
        return static(f'images/escudos/{nombre_archivo}')

    def seleccionar_oponente(self, equipo_usuario):
        candidatos = Equipo.objects.exclude(id=equipo_usuario.id).filter(ya_jugo=False)
        if not candidatos.exists():
            # Resetear el estado de los equipos para permitir nuevos partidos
            Equipo.objects.exclude(id=equipo_usuario.id).update(ya_jugo=False)
            candidatos = Equipo.objects.exclude(id=equipo_usuario.id)
        return random.choice(candidatos)

    def calcular_fuerza(self, equipo, formacion):
        bonificaciones = {'4-3-3': 10, '4-4-2': 8, '3-5-2': 7, '4-2-3-1': 9}
        return 50 + bonificaciones.get(formacion, 5)

    def generar_goles(self, ataque, defensa):
        ventaja = ataque - defensa
        return max(0, (ventaja // 10) + random.randint(-1, 2))

    def simular_eventos(self, goles_local, goles_visitante):
        eventos = []
        estadisticas_base = {
            'posesion_local': 0,
            'posesion_visitante': 0,
            'disparos_local': 0,
            'disparos_visitante': 0,
            'faltas_local': 0,
            'faltas_visitante': 0,
            'amarillas_local': 0,
            'amarillas_visitante': 0,
            'rojas_local': 0,
            'rojas_visitante': 0,
            'paradas_local': 0,
            'paradas_visitante': 0,
            'corners_local': 0,
            'corners_visitante': 0,
        }
        estadisticas_minuto_a_minuto = {i: estadisticas_base.copy() for i in range(91)}

        minutos_disponibles = list(range(1, 91))
        tipos_evento = ['gol', 'amarilla', 'roja', 'parada', 'lesion', 'poste']
        pesos_evento = [7, 15, 5, 12, 3, 7]

        for _ in range(random.randint(10, 20)):
            if not minutos_disponibles:
                break
            minuto = minutos_disponibles.pop(random.randint(0, len(minutos_disponibles) - 1))
            tipo = random.choices(tipos_evento, weights=pesos_evento, k=1)[0]
            equipo = random.choice(['local', 'visitante'])

            evento = {
                'minuto': minuto,
                'tipo': tipo,
                'equipo': equipo,
                'jugador': f"Jugador {random.randint(1, 11)}"
            }
            eventos.append(evento)

            # Actualizamos estadísticas a partir de ese minuto en adelante
            for m in range(minuto, 91):
                self.actualizar_estadisticas_evento(estadisticas_minuto_a_minuto[m], tipo, equipo)

        # Además, generamos una posesión progresiva
        for m in range(1, 91):
            estadisticas_minuto_a_minuto[m]['posesion_local'] = random.randint(40, 60)
            estadisticas_minuto_a_minuto[m]['posesion_visitante'] = 100 - estadisticas_minuto_a_minuto[m]['posesion_local']

        eventos = sorted(eventos, key=lambda e: e['minuto'])
        return {
            'eventos': eventos,
            'estadisticas_minuto_a_minuto': estadisticas_minuto_a_minuto,
            'estadisticas_final': estadisticas_minuto_a_minuto[90]
        }

    def obtener_impacto_estadistica(self, tipo, equipo):
        mapeo = {
            'gol': {f'disparos_{equipo}': 1},
            'amarilla': {f'amarillas_{equipo}': 1},
            'roja': {f'rojas_{equipo}': 1},
            'parada': {f'paradas_{equipo}': 1},
            'lesion': {},
            'poste': {f'disparos_{equipo}': 1}
        }
        return mapeo.get(tipo, {})

    def actualizar_estadisticas_evento(self, estadisticas, tipo, equipo):
        mapeo = {
            'gol': f'disparos_{equipo}',
            'amarilla': f'amarillas_{equipo}',
            'roja': f'rojas_{equipo}',
            'parada': f'paradas_{equipo}',
            'poste': f'disparos_{equipo}',
            'lesion': f'faltas_{equipo}'
        }
        if tipo in mapeo:
            estadisticas[mapeo[tipo]] += 1

    def actualizar_estadisticas_equipos(self, local, visitante, goles_local, goles_visitante):
        # Actualizar partidos jugados
        local.partidos_jugados += 1
        visitante.partidos_jugados += 1

        # Actualizar resultados
        if goles_local > goles_visitante:
            local.puntos += 3  # Victoria
            local.partidos_ganados += 1
            visitante.partidos_perdidos += 1
        elif goles_local < goles_visitante:
            visitante.puntos += 3  # Victoria
            visitante.partidos_ganados += 1
            local.partidos_perdidos += 1
        else:
            local.puntos += 1  # Empate
            visitante.puntos += 1
            local.partidos_empatados += 1
            visitante.partidos_empatados += 1

        # Guardar cambios solo al final
        local.save()
        visitante.save()

    def definir_resultado(self, goles_local, goles_visitante):
        if goles_local > goles_visitante:
            return 'victoria'
        if goles_local < goles_visitante:
            return 'derrota'
        return 'empate'

    def estadisticas_base(self):
        return {k: 0 for k in [
            'posesion_local', 'posesion_visitante', 'disparos_local', 'disparos_visitante',
            'faltas_local', 'faltas_visitante', 'amarillas_local', 'amarillas_visitante',
            'rojas_local', 'rojas_visitante', 'paradas_local', 'paradas_visitante',
            'corners_local', 'corners_visitante'
        ]}
