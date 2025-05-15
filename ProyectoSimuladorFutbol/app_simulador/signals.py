from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from app_simulador.management.commands.generar_calendarios import Command

@receiver(post_migrate)
def init_calendarios(sender, **kwargs):
    if sender.name == 'app_simulador':
        command = Command()
        command.handle()