from .models import Logro, UsuarioLogro


# Función para otorgar un logro a un usuario
def otorgar_logro(usuario, nombre_logro):
    try:
        # Se busca el logro por su nombre
        logro = Logro.objects.get(nombre=nombre_logro)

        # Verificar si el usuario ya tiene asignado ese logro
        if not UsuarioLogro.objects.filter(usuario=usuario, logro=logro).exists():
            # Si no lo tiene, se crea la relación entre el usuario y el logro
            UsuarioLogro.objects.create(usuario=usuario, logro=logro)
            return True
        return False
    except Logro.DoesNotExist:
        # Si el logro no existe en la base de datos, se imprime un mensaje de error
        print(f"Error: El logro '{nombre_logro}' no existe en la base de datos")
        return False


# Función para generar un calendario de partidos usando el sistema round-robin (todos contra todos)
def generar_calendario_round_robin(equipos):
    n = len(equipos)
    jornadas = {}

    equipos = list(equipos)
    if n % 2:
        equipos.append(None)  # Si hay un número impar de equipos, se agrega un equipo ficticio (descanso)

    num_jornadas = len(equipos) - 1  # Total de jornadas en la primera vuelta
    mitad = len(equipos) // 2  # Número de emparejamientos por jornada

    # Primera vuelta
    for j in range(num_jornadas):
        emparejamientos = []
        for i in range(mitad):
            equipo1 = equipos[i]
            equipo2 = equipos[-i - 1]
            # Se añade el emparejamiento solo si ambos equipos son válidos (no hay descanso)
            if equipo1 and equipo2:
                emparejamientos.append((equipo1.id, equipo2.id))
        jornadas[j + 1] = emparejamientos  # Se guarda la jornada correspondiente
        # Rotación de los equipos para la siguiente jornada (excepto el primero)
        equipos = [equipos[0]] + [equipos[-1]] + equipos[1:-1]

    # Segunda vuelta: se invierten los emparejamientos de la primera vuelta
    for j in range(1, num_jornadas + 1):
        emparejamientos_segunda = [(b, a) for (a, b) in jornadas[j]]
        jornadas[j + num_jornadas] = emparejamientos_segunda

    return jornadas
