from django.apps import AppConfig

class WorldTtanceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'WorldTtance'

    def ready(self):
        import WorldTtance.signals  # Triggers __init__.py which registers all signals
