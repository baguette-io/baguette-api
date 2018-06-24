from __future__ import unicode_literals

from django.apps import AppConfig


class QuotasConfig(AppConfig):
    name = 'boulangerie.apps.quotas'

    def ready(self):
        """
        Import the quotas signal handlers.
        """
        import boulangerie.apps.quotas.signals
