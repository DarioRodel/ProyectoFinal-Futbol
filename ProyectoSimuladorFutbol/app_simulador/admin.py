from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Equipo, Jugador, UserProfile, Lesion, Partido, Transferencia, Logro, UsuarioLogro
)

# Registro de modelos en el panel de administración

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ciudad', 'estadio', 'division', 'puntos', 'temporada_finalizada')
    list_filter = ('division', 'temporada_finalizada')
    search_fields = ('nombre', 'ciudad')
    ordering = ('-puntos',)  # Ordenar por puntos de mayor a menor


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'edad', 'posicion', 'equipo', 'valor_mercado', 'lesionado', 'suspendido')
    list_filter = ('posicion', 'lesionado', 'suspendido', 'equipo')
    search_fields = ('nombre', 'apellido', 'equipo__nombre')
    ordering = ('nombre',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'equipo_seleccionado', 'fecha_registro')
    list_filter = ('equipo_seleccionado',)
    search_fields = ('user__username', 'equipo_seleccionado__nombre')
    raw_id_fields = ('user',)  # Para buscar usuarios más fácilmente


@admin.register(Lesion)
class LesionAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'tipo_lesion', 'gravedad', 'fecha_inicio', 'fecha_fin')
    list_filter = ('tipo_lesion', 'gravedad')
    search_fields = ('jugador__nombre', 'jugador__apellido')
    ordering = ('-fecha_inicio',)


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('equipo_local', 'equipo_visitante', 'fecha', 'goles_local', 'goles_visitante', 'estado')
    list_filter = ('estado', 'equipo_local', 'equipo_visitante')
    search_fields = ('equipo_local__nombre', 'equipo_visitante__nombre')
    ordering = ('-fecha',)


@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'equipo_origen', 'equipo_destino', 'dinero', 'tipo', 'completada')
    list_filter = ('tipo', 'completada')
    search_fields = ('jugador__nombre', 'equipo_origen__nombre', 'equipo_destino__nombre')
    ordering = ('-fecha',)


@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'nivel')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(UsuarioLogro)
class UsuarioLogroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'logro', 'fecha_obtenido')
    list_filter = ('logro',)
    search_fields = ('usuario__username', 'logro__nombre')
    ordering = ('-fecha_obtenido',)