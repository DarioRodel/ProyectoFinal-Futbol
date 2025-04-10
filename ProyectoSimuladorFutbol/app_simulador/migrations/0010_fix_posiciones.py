# archivo migrations/XXXX_fix_missing_positions.py
from django.db import migrations


def actualizar_posiciones_faltantes(apps, schema_editor):
    Jugador = apps.get_model('app_simulador', 'Jugador')

    mapeo = {
        'PORTERO': 'POR',
        'DEFENSA': 'DEF',
        'MEDIOCAMPISTA': 'MED',  # ← Nueva entrada
        'DELANTERO': 'DEL',  # ← Nueva entrada
        'Mediocampista': 'MED',  # Para mayúsculas/minúsculas
        'Delantero': 'DEL'
    }

    for jugador in Jugador.objects.all():
        if jugador.posicion in mapeo:
            jugador.posicion = mapeo[jugador.posicion]
            jugador.save(update_fields=['posicion'])

class Migration(migrations.Migration):
    dependencies = [
        ('app_simulador', '0009_remove_jugador_condicion_fisica_and_more'),
    ]

    operations = [
        migrations.RunPython(actualizar_posiciones_faltantes),
    ]