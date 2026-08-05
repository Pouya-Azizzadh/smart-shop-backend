from django.urls import path

from .views import NFCTagListView

urlpatterns = [
    path("tags/", NFCTagListView.as_view(), name="nfc-tag-list"),
]
