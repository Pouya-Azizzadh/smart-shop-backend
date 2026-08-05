from django.urls import path

from .views import ActiveSessionView, CheckoutView, StartShoppingView

urlpatterns = [
    path("start/", StartShoppingView.as_view(), name="shopping-start"),
    path("checkout/", CheckoutView.as_view(), name="shopping-checkout"),
    path("active/", ActiveSessionView.as_view(), name="shopping-active"),
]
