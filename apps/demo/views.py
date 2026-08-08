from decimal import Decimal

from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.nfc.models import NFCTag
from apps.products.models import Product
from apps.users.models import User


class DemoSetupView(APIView):
    """Seed demo data and return context for the interactive UI."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@smartshop.com",
                "wallet_balance": Decimal("500.00"),
            },
        )
        if created or not user.check_password("demo12345"):
            user.set_password("demo12345")
            user.wallet_balance = Decimal("500.00")
            user.save()

        products_data = [
            ("Milk", "Fresh whole milk 1L", "2.00", "MILK-001"),
            ("Bread", "Whole grain bread", "3.50", "BREAD-001"),
            ("Eggs", "Free range eggs 12pk", "4.99", "EGGS-001"),
        ]

        for name, desc, price, sku in products_data:
            product, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "description": desc,
                    "price": Decimal(price),
                },
            )
            NFCTag.objects.get_or_create(
                basket_id=f"BASKET-{sku}",
                defaults={"assigned_product": product, "is_active": True},
            )

        nfc_tags = NFCTag.objects.select_related("assigned_product").filter(is_active=True)
        tags = [
            {
                "uuid": str(tag.uuid),
                "basket_id": tag.basket_id,
                "product": tag.assigned_product.name,
                "price": str(tag.assigned_product.price),
            }
            for tag in nfc_tags
        ]

        return Response(
            {
                "demo_user": {"username": "demo", "password": "demo12345"},
                "esp_api_key": settings.ESP_DEVICE_API_KEY,
                "nfc_tags": tags,
                "message": "Demo data is ready.",
            }
        )
