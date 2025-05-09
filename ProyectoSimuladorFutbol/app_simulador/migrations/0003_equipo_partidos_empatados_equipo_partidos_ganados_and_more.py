# Generated by Django 5.1.7 on 2025-03-22 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_simulador', '0002_equipo_puntos'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipo',
            name='partidos_empatados',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='equipo',
            name='partidos_ganados',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='equipo',
            name='partidos_jugados',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='equipo',
            name='partidos_perdidos',
            field=models.IntegerField(default=0),
        ),
    ]
