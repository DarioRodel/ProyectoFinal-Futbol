from django.urls import path
from .views import (
    IndexView, InicioView, RegistroView, LoginView, LogoutView,
    SeleccionarEquipoView, AsignarEquipoView, MenuView, FormacionEquipoView,
    NotificacionesView, SimularPartidoView, TablaLigaView, GuardarFormacionView,
    EliminarTemporadaView, ConfirmarCambioEquipoView, InformacionEquipoView, DetalleJugadorView, JugadoresEquipoView,
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('inicio/', InicioView.as_view(), name='inicio'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('seleccionar-equipo/', SeleccionarEquipoView.as_view(), name='seleccionar_equipo'),
    path('asignar-equipo/<int:equipo_id>/', AsignarEquipoView.as_view(), name='asignar_equipo'),
    path('confirmar-cambio/<int:equipo_id>/', ConfirmarCambioEquipoView.as_view(), name='confirmar_cambio'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('eliminar-temporada/', EliminarTemporadaView.as_view(), name='eliminar_temporada'),
    path('notificaciones/', NotificacionesView.as_view(), name='notificaciones'),
    path('tabla-liga/', TablaLigaView.as_view(), name='tabla_liga'),
    path('formacion-equipo/', FormacionEquipoView.as_view(), name='formacion_equipo'),
    path('guardar-formacion/', GuardarFormacionView.as_view(), name='guardar_formacion'),
    path('informacion-equipo/', InformacionEquipoView.as_view(), name='informacion_equipo'),
    path('equipo/jugadores/', JugadoresEquipoView.as_view(), name='jugadores_equipo'),
    path('jugador/<int:pk>/', DetalleJugadorView.as_view(), name='detalle_jugador'),
    path('simular-partido/', SimularPartidoView.as_view(), name='simular_partido'),

]
