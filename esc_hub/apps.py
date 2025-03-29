from django.apps import AppConfig


class EscHubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'esc_hub'

    def ready(self):
        from .signals import update_routes_on_new_hub