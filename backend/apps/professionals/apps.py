from django.apps import AppConfig


class ProfessionalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.professionals'
    
    def ready(self):
        import apps.professionals.signals  # noqa

