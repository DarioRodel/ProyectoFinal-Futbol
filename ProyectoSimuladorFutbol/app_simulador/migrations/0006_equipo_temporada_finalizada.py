# Generated by Django 5.1.7 on 2025-03-23 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_simulador', '0005_usuariologro'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipo',
            name='temporada_finalizada',
            field=models.BooleanField(default=False),
        ),
    ]
