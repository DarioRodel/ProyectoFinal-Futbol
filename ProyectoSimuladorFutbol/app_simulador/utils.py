from django.contrib.auth.models import User
from .models import Logro, UsuarioLogro

def otorgar_logro(usuario, logro_nombre):
    """
    Otorga un logro a un usuario si no lo tiene ya.
    """
    try:
        logro = Logro.objects.get(nombre=logro_nombre)
        if not UsuarioLogro.objects.filter(usuario=usuario, logro=logro).exists():
            UsuarioLogro.objects.create(usuario=usuario, logro=logro)
            return True  # Indica que el logro fue otorgado
        return False  # Indica que el usuario ya tenía el logro
    except Logro.DoesNotExist:
        return False  # Indica que el logro no existe