from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = "app.account"

    def ready(self):
        import app.account.signals  # noqa F401
