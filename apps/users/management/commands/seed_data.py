from django.core.management.base import BaseCommand
from decimal import Decimal

from apps.nfc.models import NFCTag
from apps.products.models import Product
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed database with sample data for development"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@smartshop.com",
                "wallet_balance": Decimal("500.00"),
            },
        )
        if created:
            user.set_password("demo12345")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user (demo/demo12345)"))
        else:
            self.stdout.write("Demo user already exists")

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

        self.stdout.write(self.style.SUCCESS("Seed data created successfully"))
