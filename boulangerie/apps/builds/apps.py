# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class BuildsConfig(AppConfig):
    """
    Builds definitions and constants.
    """
    name = 'boulangerie.apps.builds'

    def ready(self):
        """
        Import the builds signal handlers.
        """
        import boulangerie.apps.builds.signals
        import farine.settings
        farine.settings.load()
