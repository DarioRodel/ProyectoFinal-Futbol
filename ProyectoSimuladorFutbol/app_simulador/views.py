from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from .models import Equipo, Jugador, UserProfile, Lesion, Partido, Transferencia, Logro, UsuarioLogro
from .forms import CustomUserCreationForm, SeleccionEquipoForm, EditarEquipoForm
import random
from .utils import otorgar_logro


# Vista para la página de inicio
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


# Vista para la página de inicio de sesión
class InicioView(View):
    def get(self, request):
        return render(request, 'inicio.html')


# Vista para el registro de usuarios
class RegistroView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registro.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('inicio')
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
            return redirect('inicio')
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

        # Agregar la ruta de la imagen a cada equipo
        for equipo in equipos:
            equipo.ruta_escudo = imagenes_escudos.get(equipo.nombre, "images/escudos/barca.png")

        form = SeleccionEquipoForm(instance=perfil)
        return render(request, 'seleccion_equipo.html', {
            'form': form,
            'equipos': equipos,
        })

    def post(self, request):
        perfil = request.user.userprofile
        form = SeleccionEquipoForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('inicio')
        return render(request, 'seleccion_equipo.html', {'form': form})


# Vista para asignar un equipo
class AsignarEquipoView(LoginRequiredMixin, View):
    def get(self, request, equipo_id):
        equipo = get_object_or_404(Equipo, id=equipo_id)
        perfil = request.user.userprofile
        perfil.equipo_seleccionado = equipo
        perfil.save()

        # Otorgar el logro "Primer Equipo"
        otorgar_logro(request.user, "Primer Equipo")

        return redirect('menu')


# Vista para el menú principal
class MenuView(View):
    def get(self, request):
        equipos = Equipo.objects.order_by('-puntos')  # Ordenar por puntos (de mayor a menor)
        return render(request, 'menu.html', {'equipos': equipos})


# Vista para gestionar la formación del equipo
class FormacionEquipoView(LoginRequiredMixin, View):
    def get(self, request):
        perfil = request.user.userprofile
        equipo = perfil.equipo_seleccionado
        jugadores = Jugador.objects.filter(equipo=equipo)
        return render(request, 'formacion_equipo.html', {
            'equipo': equipo,
            'jugadores': jugadores,
        })

    def post(self, request):
        perfil = request.user.userprofile
        formacion = request.POST.get('formacion')
        perfil.formacion = formacion
        perfil.save()
        return redirect('menu')


# Vista para ver notificaciones
class NotificacionesView(LoginRequiredMixin, View):
    def get(self, request):
        logros_obtenidos = UsuarioLogro.objects.filter(usuario=request.user)
        return render(request, 'notificaciones.html', {
            'logros_obtenidos': logros_obtenidos,
        })


# Vista para simular un partido
class SimularPartidoView(View):
    def get(self, request):
        return render(request, 'simular_partido.html')

    def post(self, request):
        # Obtener el equipo del usuario
        perfil = request.user.userprofile
        equipo_usuario = perfil.equipo_seleccionado

        # Obtener los equipos que no han jugado aún
        equipos_disponibles = Equipo.objects.exclude(id=equipo_usuario.id).filter(ya_jugo=False)

        if not equipos_disponibles:
            # Si todos los equipos ya jugaron, reiniciar el estado
            Equipo.objects.update(ya_jugo=False)
            equipos_disponibles = Equipo.objects.exclude(id=equipo_usuario.id)

        # Seleccionar un oponente aleatorio
        oponente = random.choice(equipos_disponibles)

        # Simular un resultado aleatorio
        goles_usuario = random.randint(0, 5)  # Goles del equipo del usuario
        goles_oponente = random.randint(0, 5)  # Goles del oponente

        # Actualizar puntos según el resultado
        if goles_usuario > goles_oponente:
            equipo_usuario.puntos += 3  # Victoria del equipo del usuario
            equipo_usuario.partidos_ganados += 1  # Incrementar partidos ganados
        elif goles_usuario < goles_oponente:
            oponente.puntos += 3  # Victoria del oponente
        else:
            equipo_usuario.puntos += 1  # Empate
            oponente.puntos += 1  # Empate

        # Marcar los equipos como que ya jugaron
        equipo_usuario.ya_jugo = True
        oponente.ya_jugo = True

        # Guardar los cambios en la base de datos
        equipo_usuario.save()
        oponente.save()

        # Otorgar el logro "Primer Partido" si es el primer partido
        if not UsuarioLogro.objects.filter(usuario=request.user, logro__nombre="Primer Partido").exists():
            otorgar_logro(request.user, "Primer Partido")

        # Otorgar el logro "10 Victorias" si el usuario ha ganado 10 partidos
        if equipo_usuario.partidos_ganados >= 10:
            otorgar_logro(request.user, "10 Victorias")

        # Redirigir al menú después de simular el partido
        return redirect('menu')


# Vista para mostrar la tabla de la liga
class TablaLigaView(LoginRequiredMixin, View):
    def get(self, request):
        equipos = Equipo.objects.order_by('-puntos')  # Ordenar por puntos (de mayor a menor)

        # Obtener el equipo asignado por el usuario
        perfil = request.user.userprofile
        equipo_asignado = perfil.equipo_seleccionado

        # Verificar si el equipo del usuario está en primer lugar
        if equipos.first() == equipo_asignado:
            otorgar_logro(request.user, "Líder de la Liga")

        # Diccionario con las rutas de los escudos
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

        # Agregar la ruta de la imagen a cada equipo
        for equipo in equipos:
            equipo.ruta_escudo = imagenes_escudos.get(equipo.nombre, "images/escudos/barca.png")

        return render(request, 'tabla_liga.html', {
            'equipos': equipos,
            'equipo_asignado': equipo_asignado,  # Pasar el equipo asignado a la plantilla
        })


class FinalizarTemporadaView(LoginRequiredMixin, View):
    def get(self, request):
        # Obtener el equipo del usuario
        perfil = request.user.userprofile
        equipo_asignado = perfil.equipo_seleccionado

        # Marcar la temporada como finalizada
        equipo_asignado.temporada_finalizada = True
        equipo_asignado.save()

        # Otorgar el logro "Temporada Completa"
        otorgar_logro(request.user, "Temporada Completa")

        # Verificar si el equipo del usuario está en primer lugar
        equipos = Equipo.objects.order_by('-puntos')
        if equipos.first() == equipo_asignado:
            otorgar_logro(request.user, "Campeón de la Liga")

        return redirect('menu')





















# Vista para editar un equipo
class EditarEquipoView(LoginRequiredMixin, View):
    def get(self, request, equipo_id):
        perfil_usuario = request.user.userprofile
        equipo = get_object_or_404(Equipo, pk=equipo_id)

        if equipo != perfil_usuario.equipo_seleccionado:
            return redirect('dashboard')

        form = EditarEquipoForm(instance=equipo)
        return render(request, 'editar_equipo.html', {'form': form})

    def post(self, request, equipo_id):
        perfil_usuario = request.user.userprofile
        equipo = get_object_or_404(Equipo, pk=equipo_id)

        if equipo != perfil_usuario.equipo_seleccionado:
            return redirect('dashboard')

        form = EditarEquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            return redirect('detalle_equipo', equipo_id=equipo.id)
        return render(request, 'editar_equipo.html', {'form': form})


# Vista para gestionar un equipo
class GestionarEquipoView(LoginRequiredMixin, View):
    def get(self, request, equipo_id):
        perfil = request.user.userprofile
        equipo = get_object_or_404(Equipo, id=equipo_id)
        jugadores = Jugador.objects.filter(equipo=equipo)
        formaciones = [
            {'id': 1, 'nombre': '4-3-3'},
            {'id': 2, 'nombre': '4-4-2'},
            {'id': 3, 'nombre': '3-5-2'}
        ]
        return render(request, 'gestion_equipo.html', {
            'equipo': equipo,
            'jugadores': jugadores,
            'formaciones': formaciones
        })


# Vista para ver los detalles de un jugador
class DetallesJugadorView(LoginRequiredMixin, View):
    def get(self, request, jugador_id):
        jugador = get_object_or_404(Jugador, id=jugador_id)
        perfil_usuario = request.user.userprofile

        if jugador.equipo != perfil_usuario.equipo_seleccionado:
            return redirect('dashboard')

        return render(request, 'detalles_jugador.html', {'jugador': jugador})


# Vista para mostrar el resultado de un partido
class ResultadoPartidoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'resultado_partido.html')


# Vista para el mercado de fichajes
class MercadoFichajesView(LoginRequiredMixin, View):
    def get(self, request):
        jugadores = Jugador.objects.filter(equipo__division=1).exclude(equipo=request.user.userprofile.equipo_seleccionado)
        return render(request, 'mercado_fichajes.html', {'jugadores': jugadores})


# Vista para ver estadísticas
class EstadisticasView(LoginRequiredMixin, View):
    def get(self, request):
        equipo = request.user.userprofile.equipo_seleccionado
        goleadores = Jugador.objects.filter(equipo=equipo).order_by('-goles')[:5]
        lesiones = Lesion.objects.filter(jugador__equipo=equipo)
        return render(request, 'estadisticas.html', {
            'goleadores': goleadores,
            'lesiones': lesiones
        })