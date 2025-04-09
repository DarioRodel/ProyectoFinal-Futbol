# archivo migrations/XXXX_fix_missing_positions.py
from django.db import migrations


def actualizar_posiciones_faltantes(apps, schema_editor):
    Jugador = apps.get_model('app_simulador', 'Jugador')

    # Mapeo de nombres a claves correctas
    mapeo = {
        'Mediocampista': 'MED',
        'Delantero': 'DEL',
        'Medio': 'MED',
        'Atacante': 'DEL'
    }

    for jugador in Jugador.objects.all():
        if jugador.posicion in mapeo:
            jugador.posicion = mapeo[jugador.posicion]
            jugador.save(update_fields=['posicion'])


class Migration(migrations.Migration):
    dependencies = [
        ('app_simulador', '000x_previous_migration'),
    ]

    operations = [
        migrations.RunPython(actualizar_posiciones_faltantes),
    ]