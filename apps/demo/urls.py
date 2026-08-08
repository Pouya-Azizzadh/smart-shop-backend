from django.urls import path
from django.views.generic import TemplateView

from .views import DemoSetupView

urlpatterns = [
    # path("", TemplateView.as_view(template_name="demo/index.html"), name="demo-home"),
    # path("setup/", DemoSetupView.as_view(), name="demo-setup"),
]
