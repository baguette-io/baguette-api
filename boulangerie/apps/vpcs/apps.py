from django.apps import AppConfig


class VpcsConfig(AppConfig):
    name = 'boulangerie.apps.vpcs'

    def ready(self):
        """
        Import the VPC signal handlers.
        """
        import boulangerie.apps.vpcs.signals
