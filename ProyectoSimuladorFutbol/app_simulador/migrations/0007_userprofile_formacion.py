# Generated by Django 5.1.7 on 2025-03-27 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_simulador', '0006_equipo_temporada_finalizada'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='formacion',
            field=models.CharField(choices=[('4-4-2', '4-4-2'), ('4-3-3', '4-3-3'), ('3-5-2', '3-5-2'), ('4-2-3-1', '4-2-3-1')], default='4-4-2', max_length=10),
        ),
    ]
