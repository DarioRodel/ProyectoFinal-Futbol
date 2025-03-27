from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django import forms
from .models import Equipo, UserProfile

class SeleccionEquipoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['equipo_seleccionado']  # Campo que permite seleccionar un equipo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipo_seleccionado'].queryset = Equipo.objects.all()  # Mostrar todos los equipos

class EditarEquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            'presupuesto',
            'equipacion_principal',
            'equipacion_alternativa'
        ]

        labels = {
            'equipacion_principal': 'Equipación Titular',
            'equipacion_alternativa': 'Equipación Alterna'
        }

class GestionarEquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'presupuesto', 'equipacion_principal', 'equipacion_alternativa']
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Nombreo",
        max_length=150,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9@.+-_]+$',
                message='El nombre de usuario solo puede contener letras, números y los caracteres @/./+/-/_.',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        help_text="Introduce la misma contraseña para verificación.",
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']