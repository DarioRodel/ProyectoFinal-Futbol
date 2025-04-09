from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.views.generic import ListView, DetailView

from .models import Equipo, UserProfile, UsuarioLogro, Jugador
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
        perfil = request.user.userprofile
        equipo = perfil.equipo_seleccionado

        with transaction.atomic():
            if equipo:
                # Resetear estadísticas del equipo
                equipo.puntos = 0
                equipo.partidos_jugados = 0
                equipo.partidos_ganados = 0
                equipo.partidos_perdidos = 0
                equipo.partidos_empatados = 0
                equipo.temporada_finalizada = False
                equipo.ya_jugo = False
                equipo.save()

            # Eliminar equipo seleccionado
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
        perfil = self.request.user.userprofile
        equipo = perfil.equipo_seleccionado

        # Obtener el queryset base
        jugadores = self.get_queryset()

        # Agrupar por posiciones usando select_related/prefetch
        context.update({
            'equipo': equipo,
            'porteros': jugadores.filter(posicion='POR'),
            'defensas': jugadores.filter(posicion='DEF'),
            'mediocampistas': jugadores.filter(posicion='MED'),
            'delanteros': jugadores.filter(posicion='DEL')
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
class SimularPartidoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'simular_partido.html')

    def post(self, request):
        perfil = request.user.userprofile
        equipo_usuario = perfil.equipo_seleccionado

        if not equipo_usuario:
            return redirect('seleccionar_equipo')

        with transaction.atomic():
            # Lógica de simulación de partido
            equipos_disponibles = Equipo.objects.exclude(id=equipo_usuario.id).filter(ya_jugo=False)

            if not equipos_disponibles:
                Equipo.objects.update(ya_jugo=False)
                equipos_disponibles = Equipo.objects.exclude(id=equipo_usuario.id)

            oponente = random.choice(equipos_disponibles)
            goles_usuario = random.randint(0, 5)
            goles_oponente = random.randint(0, 5)

            # Actualizar resultados
            if goles_usuario > goles_oponente:
                equipo_usuario.puntos += 3
                equipo_usuario.partidos_ganados += 1
            elif goles_usuario < goles_oponente:
                oponente.puntos += 3
            else:
                equipo_usuario.puntos += 1
                oponente.puntos += 1

            equipo_usuario.ya_jugo = True
            oponente.ya_jugo = True
            equipo_usuario.save()
            oponente.save()

            # Otorgar logros
            if not UsuarioLogro.objects.filter(usuario=request.user, logro__nombre="Primer Partido").exists():
                otorgar_logro(request.user, "Primer Partido")

            if equipo_usuario.partidos_ganados >= 10:
                otorgar_logro(request.user, "10 Victorias")

        return redirect('menu')

