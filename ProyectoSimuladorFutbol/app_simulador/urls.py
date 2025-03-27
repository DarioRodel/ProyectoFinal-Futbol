from django.urls import path
from .views import (
    IndexView, InicioView, RegistroView, LoginView, LogoutView,
    SeleccionarEquipoView, AsignarEquipoView, MenuView, FormacionEquipoView,
    NotificacionesView, SimularPartidoView, TablaLigaView, EditarEquipoView,
    GestionarEquipoView, DetallesJugadorView, ResultadoPartidoView,
    MercadoFichajesView, EstadisticasView, GuardarFormacionView
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('inicio/', InicioView.as_view(), name='inicio'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('seleccionar-equipo/', SeleccionarEquipoView.as_view(), name='seleccionar_equipo'),
    path('asignar-equipo/<int:equipo_id>/', AsignarEquipoView.as_view(), name='asignar_equipo'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('formacion_equipo/', FormacionEquipoView.as_view(), name='formacion_equipo'),
    path('guardar-formacion/', GuardarFormacionView.as_view(), name='guardar_formacion'),
    path('notificaciones/', NotificacionesView.as_view(), name='notificaciones'),
    path('simular-partido/', SimularPartidoView.as_view(), name='simular_partido'),
    path('tabla-liga/', TablaLigaView.as_view(), name='tabla_liga'),




    path('editar-equipo/<int:equipo_id>/', EditarEquipoView.as_view(), name='editar_equipo'),
    path('gestionar-equipo/<int:equipo_id>/', GestionarEquipoView.as_view(), name='gestionar_equipo'),
    path('detalles-jugador/<int:jugador_id>/', DetallesJugadorView.as_view(), name='detalles_jugador'),
    path('resultado-partido/', ResultadoPartidoView.as_view(), name='resultado_partido'),
    path('mercado-fichajes/', MercadoFichajesView.as_view(), name='mercado_fichajes'),
    path('estadisticas/', EstadisticasView.as_view(), name='estadisticas'),
]
