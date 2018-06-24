"""
Projects app settings.
"""
from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """
    Project configuration and constants.
    """
    name = 'boulangerie.apps.projects'

    def ready(self):
        """
        Import the projects signal handlers.
        """
        import boulangerie.apps.projects.signals
