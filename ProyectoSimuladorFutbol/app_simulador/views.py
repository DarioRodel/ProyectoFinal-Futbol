import json
import logging
from django.templatetags.static import static
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .data.jugadores_equipos import jugadores
from .models import Equipo, UserProfile, UsuarioLogro, Jugador, Partido
from .forms import CustomUserCreationForm
import random
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
            perfil.jornada_actual = 1
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
        if perfil.equipo_seleccionado == equipos.first():
            if not UsuarioLogro.objects.filter(
                    usuario=request.user,
                    logro__nombre="Líder de la Liga"
            ).exists():
                otorgar_logro(request.user, "Líder de la Liga")

        if perfil.equipo_seleccionado.temporada_finalizada:
            if equipos.first() == perfil.equipo_seleccionado:
                otorgar_logro(request.user, "Campeón de la Liga")
        return render(request, 'menu.html', {
            'equipos': equipos,
            'equipo_asignado': perfil.equipo_seleccionado
        })


# Vista para eliminar temporada
class EliminarTemporadaView(LoginRequiredMixin, View):
    def post(self, request):
        # Resetear estadísticas de todos los equipos
        Equipo.objects.all().update(
            puntos=0,
            partidos_jugados=0,
            partidos_ganados=0,
            partidos_perdidos=0,
            partidos_empatados=0,
            goles_favor=0,
            goles_contra=0,
            temporada_finalizada=False,
            calendario=[]  # Limpiar calendario antiguo
        )

        # Eliminar equipo seleccionado en el perfil del usuario
        perfil = request.user.userprofile
        perfil.jornada_actual = 1
        perfil.equipo_seleccionado = None
        perfil.save()

        Partido.objects.all().delete()

        # Eliminar todos los logros del usuario
        UsuarioLogro.objects.filter(usuario=request.user).delete()

        # Generar nuevo calendario
        equipos = list(Equipo.objects.all().order_by('id'))
        calendario_completo = self.generar_round_robin_mejorado(equipos)

        # Asignar calendario a cada equipo
        for equipo in equipos:
            calendario_equipo = []
            for jornada in calendario_completo:
                for partido in jornada:
                    if partido[0].id == equipo.id:
                        calendario_equipo.append(partido[1].id)
                    elif partido[1].id == equipo.id:
                        calendario_equipo.append(partido[0].id)
            equipo.calendario = calendario_equipo
            equipo.save()

        return redirect('seleccionar_equipo')

    def generar_round_robin_mejorado(self, equipos):
        n = len(equipos)
        mitad = n // 2
        calendario = []
        equipos_rotantes = equipos[1:]  # Excluir el primer equipo como pivote

        for _ in range(n - 1):
            jornada = []
            jornada.append((equipos[0], equipos_rotantes[-1]))

            for i in range(mitad - 1):
                jornada.append((equipos_rotantes[i], equipos_rotantes[-i - 2]))

            calendario.append(jornada)
            equipos_rotantes = [equipos_rotantes[-1]] + equipos_rotantes[:-1]

        # Segunda vuelta
        segunda_vuelta = []
        for jornada in calendario:
            nueva_jornada = [(visitante, local) for local, visitante in jornada]
            segunda_vuelta.append(nueva_jornada)

        return calendario + segunda_vuelta


class FormacionEquipoView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile
        equipo = perfil.equipo_seleccionado

        if not equipo:
            return redirect('seleccionar_equipo')

        formaciones_config = {
            '4-4-2': {'DEF': 4, 'MED': 4, 'DEL': 2},
            '4-3-3': {'DEF': 4, 'MED': 3, 'DEL': 3},
            '3-5-2': {'DEF': 3, 'MED': 5, 'DEL': 2},
            '4-2-3-1': {'DEF': 4, 'MED': 5, 'DEL': 1}
        }

        formacion_get = request.GET.get('formacion')
        formacion_actual = formacion_get or getattr(perfil, 'formacion', '4-4-2') or '4-4-2'
        config = formaciones_config.get(formacion_actual, formaciones_config['4-4-2'])

        # Obtención de jugadores con ordenamiento manual
        defensas = list(Jugador.objects.filter(equipo=equipo, posicion='DEF'))
        mediocampistas = list(Jugador.objects.filter(equipo=equipo, posicion='MED'))
        delanteros = list(Jugador.objects.filter(equipo=equipo, posicion='DEL'))

        # Ordenar según posición específica
        orden_posiciones = {
            'DEF': ['LI', 'DC', 'LD'],
            'MED': ['MCD', 'MC', 'MCO', 'EI', 'ED'],
            'DEL': ['EI', 'CD', 'ED']
        }

        defensas.sort(key=lambda x: orden_posiciones['DEF'].index(x.posicion_especifica) if x.posicion_especifica in
                                                                                            orden_posiciones[
                                                                                                'DEF'] else 99)
        mediocampistas.sort(
            key=lambda x: orden_posiciones['MED'].index(x.posicion_especifica) if x.posicion_especifica in
                                                                                  orden_posiciones['MED'] else 99)
        delanteros.sort(key=lambda x: orden_posiciones['DEL'].index(x.posicion_especifica) if x.posicion_especifica in
                                                                                              orden_posiciones[
                                                                                                  'DEL'] else 99)

        jugadores_por_posicion = {
            'portero': Jugador.objects.filter(equipo=equipo, posicion='POR').first(),
            'defensas': defensas[:config['DEF']],
            'mediocampistas': mediocampistas[:config['MED']],
            'delanteros': delanteros[:config['DEL']]
        }

        return render(request, 'formacion_equipo.html', {
            'equipo': equipo,
            'jugadores_por_posicion': jugadores_por_posicion,
            'formacion_actual': formacion_actual
        })


class GuardarFormacionView(LoginRequiredMixin, View):
    def post(self, request):
        perfil = request.user.userprofile
        formacion = request.POST.get('formacion')
        formaciones_validas = ['4-4-2', '4-3-3', '3-5-2', '4-2-3-1']

        if formacion in formaciones_validas:
            perfil.formacion = formacion
            perfil.save()
            request.session['formacion_mensaje'] = f"✅ Formación actualizada a {formacion}"
        else:
            request.session['formacion_mensaje'] = "❌ Formación no válida"

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
        for equipo in Equipo.objects.all():
            equipo.actualizar_estadisticas()

        equipos = Equipo.objects.order_by('-puntos', '-goles_favor', 'goles_contra')
        perfil = request.user.userprofile
        equipo_asignado = perfil.equipo_seleccionado

        if equipo_asignado and equipos.first() == equipo_asignado:
            otorgar_logro(request.user, "Líder de la Liga")

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


class FinalizarTemporadaView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile
        equipo_asignado = perfil.equipo_seleccionado

        if not equipo_asignado:
            return redirect('seleccionar_equipo')

        otorgar_logro(request.user, "Temporada Completa")

        if Equipo.objects.order_by('-puntos').first() == equipo_asignado:
            otorgar_logro(request.user, "Campeón de la Liga")

        # Otorgar logro 10 Victorias si aplica
        if equipo_asignado.partidos_ganados >= 10:
            otorgar_logro(request.user, "10 Victorias")

        # Marcar temporada como finalizada
        equipo_asignado.temporada_finalizada = True
        equipo_asignado.save()

        return redirect('menu')  # O redirigir a una página de éxito


class InformacionEquipoView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile
        equipo = perfil.equipo_seleccionado

        if not equipo:
            return redirect('seleccionar_equipo')

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
            'ruta_escudo': ruta_escudo,
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

        porteros = jugadores.filter(posicion='POR').order_by('dorsal')
        defensas = jugadores.filter(posicion='DEF').order_by('dorsal')
        mediocampistas = jugadores.filter(posicion='MED').order_by('dorsal')
        delanteros = jugadores.filter(posicion='DEL').order_by('dorsal')

        context.update({
            'equipo': self.request.user.userprofile.equipo_seleccionado,
            'porteros': porteros,
            'defensas': defensas,
            'mediocampistas': mediocampistas,
            'delanteros': delanteros,
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

            if not equipo or equipo.temporada_finalizada or perfil.jornada_actual > 38:
                return redirect('seleccionar_equipo')

            jornada_actual = perfil.jornada_actual
            oponente = self.obtener_oponente_calendario(equipo, jornada_actual)

            if not oponente:
                return redirect('temporada_finalizada')

            request.session['oponente_id'] = oponente.id

            contexto = {
                'equipo_usuario': equipo,
                'escudo_usuario': self.obtener_ruta_escudo(equipo),
                'oponente': oponente,
                'escudo_oponente': self.obtener_ruta_escudo(oponente),
                'eventos_json': json.dumps([]),
                'jornada_actual': jornada_actual,
                'es_ultima_jornada': jornada_actual == 38,
                'temporada_finalizada': equipo.temporada_finalizada
            }

            return render(request, self.template_name, contexto)

        except Exception as e:
            logger.error(f"Error en GET: {str(e)}")
            return render(request, 'error.html', {'error': str(e)})

    def post(self, request):
        try:
            perfil = request.user.userprofile
            if perfil.jornada_actual > 38:
                return JsonResponse({'status': 'error', 'message': 'La temporada ya ha finalizado'}, status=400)

            equipo_usuario = perfil.equipo_seleccionado
            oponente_id = request.session.get('oponente_id')

            if not oponente_id:
                return JsonResponse({'status': 'error', 'message': 'Oponente no encontrado'}, status=400)

            oponente = Equipo.objects.get(id=oponente_id)
            jornada_actual = perfil.jornada_actual

            if Partido.objects.filter(
                    Q(equipo_local=equipo_usuario, equipo_visitante=oponente, jornada=jornada_actual) |
                    Q(equipo_local=oponente, equipo_visitante=equipo_usuario, jornada=jornada_actual)
            ).exists():
                return JsonResponse({'status': 'error', 'message': 'Ya has jugado esta jornada'}, status=400)

            # Simulación del partido
            fuerza_local = self.calcular_fuerza(equipo_usuario, perfil.formacion)
            fuerza_visitante = self.calcular_fuerza(oponente, '4-4-2')
            goles_local = self.generar_goles(fuerza_local, fuerza_visitante)
            goles_visitante = self.generar_goles(fuerza_visitante, fuerza_local)

            # Simulación de eventos con estadísticas en tiempo real
            eventos_data = self.simular_eventos(equipo_usuario, oponente, goles_local, goles_visitante)

            # Crear registro del partido
            Partido.objects.create(
                equipo_local=equipo_usuario,
                equipo_visitante=oponente,
                goles_local=goles_local,
                goles_visitante=goles_visitante,
                eventos=eventos_data['eventos'],
                estadisticas=eventos_data['estadisticas_final'],
                estado='finalizado',
                jornada=jornada_actual
            )

            # Actualizar estadísticas de equipos
            self.actualizar_estadisticas_equipos(equipo_usuario, oponente, goles_local, goles_visitante)
            self.simular_jornada_completa(jornada_actual, equipo_usuario, oponente)

            # Manejo final de temporada
            if jornada_actual == 38:
                equipo_usuario.temporada_finalizada = True
                equipo_usuario.save()
                self.otorgar_logros_finales(request.user, equipo_usuario)
                request.session.pop('oponente_id', None)
                return JsonResponse({'status': 'redirect', 'redirect_url': reverse('temporada_finalizada')})
            self.otorgar_logros_partido(request.user, equipo_usuario)
            # Actualizar jornada y preparar respuesta
            perfil.jornada_actual += 1
            perfil.save()

            respuesta = {
                'status': 'success',
                'resultado': self.definir_resultado(goles_local, goles_visitante),
                'goles_usuario': goles_local,
                'goles_oponente': goles_visitante,
                'eventos': eventos_data['eventos'],
                'estadisticas': eventos_data['estadisticas_minuto_a_minuto'],
                'jornada_actual': perfil.jornada_actual,
                'oponente': {
                    'nombre': oponente.nombre,
                    'escudo': self.obtener_ruta_escudo(oponente)
                }
            }

            request.session.pop('oponente_id', None)
            return JsonResponse(respuesta, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            logger.error(f"Error en POST: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def simular_jornada_completa(self, jornada, equipo_usuario, oponente_usuario):
        # Simular todos los partidos de la jornada excepto el del usuario
        equipos = Equipo.objects.all()

        for equipo in equipos:
            try:
                oponente_id = equipo.calendario[jornada - 1]
                oponente = Equipo.objects.get(id=oponente_id)

                # Saltar si es el partido del usuario
                if {equipo.id, oponente.id} == {equipo_usuario.id, oponente_usuario.id}:
                    continue

                # Verificar si el partido ya existe
                if not Partido.objects.filter(
                        Q(equipo_local=equipo, equipo_visitante=oponente, jornada=jornada) |
                        Q(equipo_local=oponente, equipo_visitante=equipo, jornada=jornada)
                ).exists():

                    # Simular solo si el equipo es local en su calendario
                    if equipo.calendario[jornada - 1] == oponente.id:
                        fuerza_local = self.calcular_fuerza(equipo, '4-4-2')
                        fuerza_visitante = self.calcular_fuerza(oponente, '4-4-2')
                        goles_local = self.generar_goles(fuerza_local, fuerza_visitante)
                        goles_visitante = self.generar_goles(fuerza_visitante, fuerza_local)

                        Partido.objects.create(
                            equipo_local=equipo,
                            equipo_visitante=oponente,
                            goles_local=goles_local,
                            goles_visitante=goles_visitante,
                            jornada=jornada,
                            estado='finalizado'
                        )
                        self.actualizar_estadisticas_equipos(equipo, oponente, goles_local, goles_visitante)

            except IndexError:
                continue

    def otorgar_logros_finales(self, usuario, equipo):
        """Otorga los logros al finalizar la temporada"""
        # Logro Temporada Completa
        otorgar_logro(usuario, "Temporada Completa")

        # Logro Campeón de Liga
        equipos_ordenados = Equipo.objects.order_by('-puntos')
        if equipos_ordenados.first() == equipo:
            otorgar_logro(usuario, "Campeón de la Liga")

    def obtener_oponente_calendario(self, equipo, jornada_actual):
        # Obtener del calendario almacenado en el equipo
        try:
            oponente_id = equipo.calendario[jornada_actual - 1]  # Los arrays empiezan en 0
            return Equipo.objects.get(id=oponente_id)
        except (IndexError, Equipo.DoesNotExist):
            return None

    def es_local(self, equipo, jornada_actual):
        calendario = self.obtener_calendario_global()
        partidos_jornada = calendario.get(jornada_actual, [])

        for local_id, visitante_id in partidos_jornada:
            if equipo.id == local_id:
                return True
            elif equipo.id == visitante_id:
                return False
        return None

    def otorgar_logros_partido(self, user, equipo):
        if not Partido.objects.filter(
                Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
        ).exclude(estado='pendiente').exists():
            otorgar_logro(user, "Primer Partido")

    def obtener_ruta_escudo(self, equipo):
        if not equipo:
            return static('images/escudos/realmadrid.png')
        nombre_archivo = self.ESCUDOS_MAP.get(equipo.nombre, 'realmadrid.png')
        return static(f'images/escudos/{nombre_archivo}')

    def calcular_fuerza(self, equipo, formacion):
        bonificaciones = {
            '4-3-3': {'ataque': 12, 'defensa': 8},
            '4-4-2': {'ataque': 9, 'defensa': 10},
            '3-5-2': {'ataque': 10, 'defensa': 9},
            '4-2-3-1': {'ataque': 11, 'defensa': 8}
        }
        return bonificaciones.get(formacion, {'ataque': 50, 'defensa': 50})

    def generar_goles(self, fuerza_ataque, fuerza_defensa):
        base = (fuerza_ataque['ataque'] * 0.4 - fuerza_defensa['defensa'] * 0.3) / 15
        probabilidad_gol = max(0.1, min(0.3, base))
        return sum(1 for _ in range(15) if random.random() < probabilidad_gol)

    def crear_evento(self, minuto, tipo, equipo, jugador):
        # Verificar datos completos del jugador
        if not jugador or not all(key in jugador for key in ['nombre', 'apellido', 'dorsal']):
            return None  # No crear eventos inválidos

        return {
            'minuto': minuto,
            'tipo': tipo,
            'equipo': equipo,
            'jugador': f"{jugador['nombre']} {jugador['apellido']}",
            'dorsal': jugador['dorsal']
        }

    def simular_eventos(self, equipo_local, equipo_visitante, goles_local, goles_visitante):
        eventos = []
        estadisticas_minuto_a_minuto = []
        estadisticas_actual = self.estadisticas_base()
        ultimo_evento_minuto = -20  # Para evitar eventos muy seguidos

        # Generar eventos de goles
        for _ in range(goles_local):
            minuto = self.generar_minuto_espaciado(eventos, 3)
            jugador = self.obtener_jugador_para_evento(jugadores[equipo_local.nombre], 'gol')
            eventos.append(self.crear_evento(minuto, 'gol', 'local', jugador))

        for _ in range(goles_visitante):
            minuto = self.generar_minuto_espaciado(eventos, 3)
            jugador = self.obtener_jugador_para_evento(jugadores[equipo_visitante.nombre], 'gol')
            eventos.append(self.crear_evento(minuto, 'gol', 'visitante', jugador))

        # Simular otros eventos minuto a minuto
        for minuto in range(1, 91):
            minuto_data = {
                'minuto': minuto,
                'estadisticas': self.estadisticas_base(),
                'eventos': []
            }

            # Solo generar eventos nuevos si ha pasado tiempo desde el último
            if minuto - ultimo_evento_minuto >= 2:
                # Probabilidades de eventos
                if random.random() < 0.10:  # Faltas
                    equipo = random.choice(['local', 'visitante'])
                    tipo = 'falta'
                    jugador = self.obtener_jugador_para_evento(
                        jugadores[equipo_local.nombre if equipo == 'local' else equipo_visitante.nombre],
                        tipo
                    )
                    if jugador:
                        evento = self.crear_evento(minuto, tipo, equipo, jugador)
                        eventos.append(evento)
                        ultimo_evento_minuto = minuto

                if random.random() < 0.04:  # Tarjetas amarillas
                    equipo = random.choice(['local', 'visitante'])
                    tipo = 'amarilla'
                    jugador = self.obtener_jugador_para_evento(
                        jugadores[equipo_local.nombre if equipo == 'local' else equipo_visitante.nombre],
                        tipo
                    )
                    if jugador:
                        evento = self.crear_evento(minuto, tipo, equipo, jugador)
                        eventos.append(evento)
                        ultimo_evento_minuto = minuto

                if random.random() < 0.015:  # Tarjetas rojas
                    equipo = random.choice(['local', 'visitante'])
                    tipo = 'roja'
                    jugador = self.obtener_jugador_para_evento(
                        jugadores[equipo_local.nombre if equipo == 'local' else equipo_visitante.nombre],
                        tipo
                    )
                    if jugador:
                        evento = self.crear_evento(minuto, tipo, equipo, jugador)
                        eventos.append(evento)
                        ultimo_evento_minuto = minuto

                if random.random() < 0.08:  # Paradas del portero
                    equipo = 'visitante' if random.choice([True, False]) else 'local'
                    tipo = 'parada'
                    jugador = self.obtener_jugador_para_evento(
                        jugadores[equipo_visitante.nombre if equipo == 'visitante' else equipo_local.nombre],
                        tipo
                    )
                    if jugador:
                        evento = self.crear_evento(minuto, tipo, equipo, jugador)
                        eventos.append(evento)
                        ultimo_evento_minuto = minuto

                if random.random() < 0.01:  # Lesiones
                    equipo = random.choice(['local', 'visitante'])
                    tipo = 'lesion'
                    jugador = self.obtener_jugador_para_evento(
                        jugadores[equipo_local.nombre if equipo == 'local' else equipo_visitante.nombre],
                        tipo
                    )
                    if jugador:
                        evento = self.crear_evento(minuto, tipo, equipo, jugador)
                        eventos.append(evento)
                        ultimo_evento_minuto = minuto
                        # Marcar jugador como lesionado
                        jugador['lesionado'] = True

                if random.random() < 0.05:  # Córners
                    equipo = random.choice(['local', 'visitante'])
                    tipo = 'corner'
                    jugador = self.obtener_jugador_para_evento(
                        jugadores[equipo_local.nombre if equipo == 'local' else equipo_visitante.nombre],
                        tipo
                    )
                    if jugador:
                        evento = self.crear_evento(minuto, tipo, equipo, jugador)
                        eventos.append(evento)
                        ultimo_evento_minuto = minuto

                if random.random() < 0.02:  # Disparos al poste
                    equipo = random.choice(['local', 'visitante'])
                    tipo = 'poste'
                    jugador = self.obtener_jugador_para_evento(
                        jugadores[equipo_local.nombre if equipo == 'local' else equipo_visitante.nombre],
                        tipo
                    )
                    if jugador:
                        evento = self.crear_evento(minuto, tipo, equipo, jugador)
                        eventos.append(evento)
                        ultimo_evento_minuto = minuto

            # Actualizar estadísticas para este minuto
            for key in estadisticas_actual:
                minuto_data['estadisticas'][key] = estadisticas_actual[key]

            # Procesar eventos de este minuto
            eventos_minuto = [e for e in eventos if e['minuto'] == minuto]
            for evento in eventos_minuto:
                self.actualizar_estadisticas_evento(estadisticas_actual, evento['tipo'], evento['equipo'])
                minuto_data['eventos'].append(evento)

            # Actualizar posesión de balón
            posesion_local = estadisticas_actual['posesion_local']
            cambio_posesion = random.choice([-2, -1, 0, 1, 2])
            nueva_posesion = max(35, min(65, posesion_local + cambio_posesion))
            estadisticas_actual['posesion_local'] = nueva_posesion
            estadisticas_actual['posesion_visitante'] = 100 - nueva_posesion

            # Añadir disparos aleatorios
            if random.random() < 0.06:
                equipo = 'local' if random.random() < nueva_posesion / 100 else 'visitante'
                estadisticas_actual[f'disparos_{equipo}'] += 1

            estadisticas_minuto_a_minuto.append(minuto_data)

        return {
            'eventos': sorted(eventos, key=lambda x: x['minuto']),
            'estadisticas_final': estadisticas_actual,
            'estadisticas_minuto_a_minuto': estadisticas_minuto_a_minuto
        }

    def otorgar_logros_partido(self, user, equipo):
        """Otorga los logros relacionados con partidos"""
        # Verificar si es el primer partido del usuario
        partidos_count = Partido.objects.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
            estado='finalizado'
        ).count()

        if partidos_count == 1:
            otorgar_logro(user, "Primer Partido")

        # Verificar si ha alcanzado 10 victorias
        if equipo.partidos_ganados >= 10:
            otorgar_logro(user, "10 Victorias")
    def generar_minuto_espaciado(self, eventos_existentes, espaciado_minimo):
        """Genera un minuto que esté al menos a X minutos de otros eventos"""
        intentos = 0
        while intentos < 50:  # Máximo 50 intentos para evitar bucle infinito
            minuto = random.randint(1, 90)

            # Verificar espaciado con otros eventos
            valido = True
            for evento in eventos_existentes:
                if abs(evento['minuto'] - minuto) < espaciado_minimo:
                    valido = False
                    break

            if valido:
                return minuto

            intentos += 1

        # Si no encontramos uno perfecto, devolvemos uno aleatorio
        return random.randint(1, 90)

    def obtener_jugador_para_evento(self, datos_equipo, tipo_evento):
        posiciones = {
            'gol': ['DEL', 'MED'],
            'amarilla': ['DEF', 'MED'],
            'roja': ['DEF', 'MED'],
            'parada': ['POR'],
            'falta': ['DEF', 'MED'],
            'lesion': None,
            'poste': ['DEL', 'MED'],
            'corner': ['DEL', 'MED']
        }.get(tipo_evento, None)

        jugadores_validos = []
        for pos in (posiciones if posiciones else ['DEL', 'MED', 'DEF', 'POR']):
            for jugador in datos_equipo.get(pos, []):
                # Validar datos mínimos del jugador
                if all(key in jugador for key in ['nombre', 'apellido', 'dorsal']):
                    jugadores_validos.append(jugador)

        return random.choice(jugadores_validos) if jugadores_validos else None

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
        actualizaciones = {
            'gol': [('goles', 1), ('disparos', 1)],
            'amarilla': [('amarillas', 1)],
            'roja': [('rojas', 1), ('amarillas', 1)],
            'parada': [('paradas', 1)],
            'falta': [('faltas', 1)],
            'lesion': [('faltas', 2)],
            'poste': [('disparos', 1)],
            'corner': [('corners', 1)]
        }.get(tipo, [])

        for stat, incremento in actualizaciones:
            key = f"{stat}_{equipo}"
            estadisticas[key] += incremento

    def actualizar_estadisticas_equipos(self, local, visitante, goles_local, goles_visitante):
        local.partidos_jugados += 1
        local.goles_favor += goles_local
        local.goles_contra += goles_visitante
        visitante.partidos_jugados += 1
        visitante.goles_favor += goles_visitante
        visitante.goles_contra += goles_local

        if goles_local > goles_visitante:
            local.puntos += 3
            local.partidos_ganados += 1
            visitante.partidos_perdidos += 1
        elif goles_local < goles_visitante:
            visitante.puntos += 3
            visitante.partidos_ganados += 1
            local.partidos_perdidos += 1
        else:
            local.puntos += 1
            visitante.puntos += 1
            local.partidos_empatados += 1
            visitante.partidos_empatados += 1
        if local.partidos_ganados >= 10:
            otorgar_logro(self.request.user, "10 Victorias")
        if visitante == self.request.user.userprofile.equipo_seleccionado and visitante.partidos_ganados >= 10:
            otorgar_logro(self.request.user, "10 Victorias")
        local.save()
        visitante.save()


    def definir_resultado(self, goles_local, goles_visitante):
        if goles_local > goles_visitante:
            return 'victoria'
        if goles_local < goles_visitante:
            return 'derrota'
        return 'empate'

    def estadisticas_base(self):
        return {
            'posesion_local': 50,
            'posesion_visitante': 50,
            'disparos_local': 0,
            'disparos_visitante': 0,
            'goles_local': 0,
            'goles_visitante': 0,
            'faltas_local': 0,
            'faltas_visitante': 0,
            'amarillas_local': 0,
            'amarillas_visitante': 0,
            'rojas_local': 0,
            'rojas_visitante': 0,
            'paradas_local': 0,
            'paradas_visitante': 0,
            'corners_local': 0,
            'corners_visitante': 0
        }


class TemporadaFinalizadaView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile
        equipo = perfil.equipo_seleccionado

        if not equipo or not equipo.temporada_finalizada:
            return redirect('menu')

        context = {
            'equipo': equipo,
            'puntos_totales': equipo.puntos,
            'victorias': equipo.partidos_ganados,
            'derrotas': equipo.partidos_perdidos,
            'logro_temporada_completa': UsuarioLogro.objects.filter(
                usuario=request.user,
                logro__nombre="Temporada Completa"
            ).exists()
        }

        return render(request, 'temporada_finalizada.html', context)