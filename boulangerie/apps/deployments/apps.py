# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DeploymentsConfig(AppConfig):
    """
    Deployments definitions and constants.
    """
    name = 'boulangerie.apps.deployments'

    def ready(self):
        """
        Import the deployments signal handlers.
        """
        import boulangerie.apps.deployments.signals
        import farine.settings
        farine.settings.load()
