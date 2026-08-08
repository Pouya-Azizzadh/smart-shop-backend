from django.urls import path

from .views import DemoSetupView

urlpatterns = [
    path("", DemoSetupView.as_view(), name="demo-setup-api"),
]
