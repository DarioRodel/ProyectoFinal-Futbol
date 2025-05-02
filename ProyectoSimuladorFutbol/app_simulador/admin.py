from django.contrib import admin
from .models import (
    Equipo, Jugador, UserProfile, Lesion, Partido, Transferencia, Logro, UsuarioLogro
)


# Registro del modelo Equipo en el panel de administración
@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista de equipos
    list_display = ('nombre', 'ciudad', 'estadio', 'division', 'puntos', 'temporada_finalizada')

    # Filtros para poder filtrar equipos por division y si han finalizado la temporada
    list_filter = ('division', 'temporada_finalizada')

    # Campos por los cuales se puede buscar un equipo
    search_fields = ('nombre', 'ciudad')

    # Orden por defecto, en este caso por puntos en orden descendente
    ordering = ('-puntos',)


# Registro del modelo Jugador en el panel de administración
@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista de jugadores
    list_display = ('nombre', 'apellido', 'edad', 'posicion', 'equipo', 'valor_mercado', 'lesionado', 'suspendido')

    # Filtros para poder filtrar jugadores por posición, lesión, suspensión y equipo
    list_filter = ('posicion', 'lesionado', 'suspendido', 'equipo')

    # Campos por los cuales se puede buscar un jugador
    search_fields = ('nombre', 'apellido', 'equipo__nombre')

    # Orden por defecto, en este caso por nombre
    ordering = ('nombre',)


# Registro del modelo UserProfile en el panel de administración
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista de perfiles de usuario
    list_display = ('user', 'equipo_seleccionado', 'fecha_registro')

    # Filtro para poder filtrar por el equipo seleccionado
    list_filter = ('equipo_seleccionado',)

    # Campos por los cuales se puede buscar un perfil de usuario
    search_fields = ('user__username', 'equipo_seleccionado__nombre')

    # Muestra el ID de usuario como campo "raw" para facilitar la selección
    raw_id_fields = ('user',)


# Registro del modelo Lesion en el panel de administración
@admin.register(Lesion)
class LesionAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista de lesiones
    list_display = ('jugador', 'tipo_lesion', 'gravedad', 'fecha_inicio', 'fecha_fin')

    # Filtros para poder filtrar por tipo de lesión y gravedad
    list_filter = ('tipo_lesion', 'gravedad')

    # Campos por los cuales se puede buscar una lesión
    search_fields = ('jugador__nombre', 'jugador__apellido')

    # Orden por defecto, en este caso por fecha de inicio de la lesión
    ordering = ('-fecha_inicio',)


# Registro del modelo Partido en el panel de administración
@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista de partidos
    list_display = ('equipo_local', 'equipo_visitante', 'fecha', 'goles_local', 'goles_visitante', 'estado')

    # Filtros para poder filtrar por estado y por equipos involucrados
    list_filter = ('estado', 'equipo_local', 'equipo_visitante')

    # Campos por los cuales se puede buscar un partido
    search_fields = ('equipo_local__nombre', 'equipo_visitante__nombre')

    # Orden por defecto, en este caso por la fecha del partido
    ordering = ('-fecha',)


# Registro del modelo Transferencia en el panel de administración
@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista de transferencias
    list_display = ('jugador', 'equipo_origen', 'equipo_destino', 'dinero', 'tipo', 'completada')

    # Filtros para poder filtrar por tipo de transferencia y si fue completada
    list_filter = ('tipo', 'completada')

    # Campos por los cuales se puede buscar una transferencia
    search_fields = ('jugador__nombre', 'equipo_origen__nombre', 'equipo_destino__nombre')

    # Orden por defecto, en este caso por fecha de la transferencia
    ordering = ('-fecha',)


# Registro del modelo Logro en el panel de administración
@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista de logros
    list_display = ('nombre', 'descripcion', 'nivel')

    # Campos por los cuales se puede buscar un logro
    search_fields = ('nombre',)

    # Orden por defecto, en este caso por nombre del logro
    ordering = ('nombre',)


# Registro del modelo UsuarioLogro en el panel de administración
@admin.register(UsuarioLogro)
class UsuarioLogroAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista de logros de usuarios
    list_display = ('usuario', 'logro', 'fecha_obtenido')

    # Filtro para poder filtrar por logro
    list_filter = ('logro',)

    # Campos por los cuales se puede buscar un logro de usuario
    search_fields = ('usuario__username', 'logro__nombre')

    # Orden por defecto, en este caso por la fecha en que se obtuvo el logro
    ordering = ('-fecha_obtenido',)
