# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    name = 'boulangerie.apps.organizations'

    def ready(self):
        """
        Import the organizations signal handlers.
        """
        import boulangerie.apps.organizations.signals
