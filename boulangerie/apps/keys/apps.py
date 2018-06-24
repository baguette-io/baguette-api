from django.apps import AppConfig


class KeysConfig(AppConfig):
    name = 'boulangerie.apps.keys'

    def ready(self):
        """
        Import the key signal handlers.
        """
        import boulangerie.apps.keys.signals
