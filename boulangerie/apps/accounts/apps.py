from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'boulangerie.apps.accounts'

    def ready(self):
        """
        Import the accounts signal handlers.
        """
        import boulangerie.apps.accounts.signals
