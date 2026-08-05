from .base import *  # noqa: F403

DEBUG = True
USE_INMEMORY_CHANNEL_LAYER = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

ESP_MQTT_ENABLED = False
