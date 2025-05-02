from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime


class Equipo(models.Model):
    POSICIONES_LIGA = [(1, 'Primera División')]

    nombre = models.CharField(max_length=100, unique=True)
    ciudad = models.CharField(max_length=100)
    estadio = models.CharField(max_length=100)
    ya_jugo = models.BooleanField(default=False)
    fundacion = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1800),
            MaxValueValidator(datetime.now().year)
        ]
    )
    division = models.IntegerField(choices=POSICIONES_LIGA, default=1)
    presupuesto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    equipacion_principal = models.CharField(
        max_length=50,
        validators=[RegexValidator(
            regex='^[a-zA-ZáéíóúñÁÉÍÓÚÑ ]+$',
            message='Solo se permiten letras y espacios'
        )]
    )
    equipacion_alternativa = models.CharField(
        max_length=50,
        validators=[RegexValidator(
            regex='^[a-zA-ZáéíóúñÁÉÍÓÚÑ ]+$',
            message='Solo se permiten letras y espacios'
        )]
    )
    imagen_escudo = models.ImageField(upload_to='escudos/', null=True, blank=True)
    ruta_escudo = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    puntos = models.IntegerField(default=0)
    partidos_jugados = models.IntegerField(default=0)
    partidos_ganados = models.IntegerField(default=0)
    partidos_perdidos = models.IntegerField(default=0)
    partidos_empatados = models.IntegerField(default=0)
    goles_favor = models.IntegerField(default=0)  # Goles a favor
    goles_contra = models.IntegerField(default=0)  # Goles en contra
    temporada_finalizada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class Jugador(models.Model):
    POSICIONES = [
        ('POR', 'Portero'),
        ('DEF', 'Defensa'),
        ('MED', 'Mediocampista'),
        ('DEL', 'Delantero')
    ]
    POSICIONES_ESPECIFICAS = [
        # Defensas
        ('DC', 'Defensa Central'),
        ('LD', 'Lateral Derecho'),
        ('LI', 'Lateral Izquierdo'),
        # Mediocampistas
        ('MCD', 'Mediocentro Defensivo'),
        ('MC', 'Mediocentro'),
        ('MCO', 'Mediocentro Ofensivo'),
        # Delanteros
        ('CD', 'Centrodelantero'),
        ('ED', 'Extremo Derecho'),
        ('EI', 'Extremo Izquierdo'),
        ('SD', 'Segundo Delantero')
    ]
    posicion_especifica = models.CharField(
        max_length=3,
        choices=POSICIONES_ESPECIFICAS,
        default='DC'  # Asegurar un valor por defecto
    )
    posicion = models.CharField(max_length=3, choices=POSICIONES)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    edad = models.IntegerField(
        validators=[
            MinValueValidator(16),
            MaxValueValidator(50)
        ]
    )
    nacionalidad = models.CharField(max_length=50)
    valor_mercado = models.DecimalField(max_digits=10, decimal_places=2)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='jugadores')
    dorsal = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(99)
        ],
        null=True,
        blank=True
    )
    lesionado = models.BooleanField(default=False)
    suspendido = models.BooleanField(default=False)

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return self.nombre_completo


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    equipo_seleccionado = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True)
    logros_desbloqueados = models.ManyToManyField('Logro', blank=True)
    jornada_actual = models.IntegerField(default=1)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    formacion = models.CharField(
        max_length=10,
        default='4-4-2',
        choices=[
            ('4-4-2', '4-4-2'),
            ('4-3-3', '4-3-3'),
            ('3-5-2', '3-5-2'),
            ('4-2-3-1', '4-2-3-1')
        ]
    )


class Lesion(models.Model):
    TIPOS_LESION = [
        ('Muscular', 'Muscular'),
        ('Ósea', 'Ósea'),
        ('Articular', 'Articular'),
        ('Otra', 'Otra')
    ]

    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    gravedad = models.CharField(max_length=50, choices=[('Leve', 'Leve'), ('Grave', 'Grave')])
    tipo_lesion = models.CharField(max_length=50, choices=TIPOS_LESION, default='Muscular')
    descripcion = models.TextField()


class Partido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('jugando', 'Jugando'),
        ('finalizado', 'Finalizado'),
    ]

    equipo_local = models.ForeignKey('Equipo', on_delete=models.CASCADE, related_name='partidos_como_local')
    equipo_visitante = models.ForeignKey('Equipo', on_delete=models.CASCADE, related_name='partidos_como_visitante')
    fecha = models.DateTimeField(auto_now_add=True)
    goles_local = models.PositiveIntegerField(default=0)
    goles_visitante = models.PositiveIntegerField(default=0)
    eventos = models.JSONField(default=dict, blank=True)
    estadisticas = models.JSONField(default=dict, blank=True)
    jornada = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} (Jornada {self.jornada})"


class Transferencia(models.Model):
    TIPOS_TRANSFERENCIA = [
        ('Compra', 'Compra'),
        ('Venta', 'Venta'),
        ('Préstamo', 'Préstamo')
    ]

    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    equipo_origen = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='transferencias_salientes')
    equipo_destino = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='transferencias_entrantes')
    dinero = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    fecha = models.DateField(auto_now_add=True)
    completada = models.BooleanField(default=False)
    tipo = models.CharField(max_length=50, choices=TIPOS_TRANSFERENCIA, default='Compra')


class Logro(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    requisito = models.CharField(max_length=200)
    efecto_quimica = models.IntegerField(default=0)
    icono = models.CharField(max_length=100)
    nivel = models.IntegerField(default=1)


class UsuarioLogro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_obtenido = models.DateTimeField(auto_now_add=True)
