from rest_framework import permissions
from rest_framework.permissions import BasePermission


class ESPDevicePermission(BasePermission):
    """Allow ESP devices authenticated via API key header."""

    message = "Invalid or missing ESP device API key."

    def has_permission(self, request, view):
        api_key = request.headers.get("X-ESP-API-Key", "")
        from django.conf import settings

        return api_key == settings.ESP_DEVICE_API_KEY
