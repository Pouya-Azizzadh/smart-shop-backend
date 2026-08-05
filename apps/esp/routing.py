from django.urls import re_path

from .consumers import ESPDeviceConsumer, ShoppingSessionConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/shopping/session/(?P<session_id>\d+)/$",
        ShoppingSessionConsumer.as_asgi(),
    ),
    re_path(
        r"ws/shopping/user/$",
        ShoppingSessionConsumer.as_asgi(),
    ),
    re_path(
        r"ws/esp/events/$",
        ESPDeviceConsumer.as_asgi(),
    ),
]
