from django.apps import AppConfig


class EspConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.esp"
    label = "esp"

    def ready(self):
        from .mqtt_client import start_mqtt_listener

        start_mqtt_listener()
