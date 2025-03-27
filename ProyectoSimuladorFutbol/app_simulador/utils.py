from django.utils import timezone
from .models import Logro, UsuarioLogro

def otorgar_logro(usuario, nombre_logro):
    try:
        logro = Logro.objects.get(nombre=nombre_logro)
        # Verificar si el usuario ya tiene el logro
        if not UsuarioLogro.objects.filter(usuario=usuario, logro=logro).exists():
            UsuarioLogro.objects.create(usuario=usuario, logro=logro)
            return True
        return False
    except Logro.DoesNotExist:
        print(f"Error: El logro '{nombre_logro}' no existe en la base de datos")
        return False