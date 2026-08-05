from django.urls import path

from .views import ESPEventView

urlpatterns = [
    path("events/", ESPEventView.as_view(), name="esp-events"),
]
