from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Equipo, UserProfile


# Formulario para seleccionar un equipo
class SeleccionEquipoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['equipo_seleccionado']  # Campo que será mostrado en el formulario

    # Modificar la consulta para 'equipo_seleccionado', mostrando todos los equipos disponibles
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipo_seleccionado'].queryset = Equipo.objects.all()  # Mostrar todos los equipos


# Formulario para editar un equipo existente
class EditarEquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            'presupuesto',  # Campo para modificar el presupuesto del equipo
            'equipacion_principal',  # Campo para la equipación principal
            'equipacion_alternativa'  # Campo para la equipación alternativa
        ]

        # Etiquetas personalizadas para los campos
        labels = {
            'equipacion_principal': 'Equipación Titular',
            'equipacion_alternativa': 'Equipación Alternativa'
        }


# Formulario para gestionar todos los aspectos de un equipo (modificar nombre, presupuesto y equipaciones)
class GestionarEquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'presupuesto', 'equipacion_principal', 'equipacion_alternativa']


# Formulario personalizado para la creación de un nuevo usuario (registro)
class CustomUserCreationForm(UserCreationForm):
    # Campo para el nombre de usuario
    username = forms.CharField(
        label="Nombreo",
        max_length=150,
        validators=[  # Validador para el nombre de usuario (solo letras, números y algunos caracteres especiales)
            RegexValidator(
                regex='^[a-zA-Z0-9@.+-_]+$',  # Expresión regular para validar caracteres permitidos
                message='El nombre de usuario solo puede contener letras, números y los caracteres @/./+/-/_.',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
    )

    # Campo para el correo electrónico
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
    )

    # Campo para la contraseña (Primera contraseña)
    password1 = forms.CharField(
        label="Contraseña",  # Título del campo
        strip=False,  # Elimina espacios antes o después de la contraseña
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),  # Estilo del campo
    )

    # Campo para la confirmación de la contraseña
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,  # Elimina espacios antes o después
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        help_text="Introduce la misma contraseña para verificación.",
    )

    # Información sobre el modelo al cual este formulario está asociado
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
