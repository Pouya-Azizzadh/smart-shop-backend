import pytest
from decimal import Decimal

from apps.nfc.models import NFCTag
from apps.products.models import Product
from apps.users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        wallet_balance=Decimal("100.00"),
    )


@pytest.fixture
def product(db):
    return Product.objects.create(
        name="Milk",
        description="Fresh milk 1L",
        price=Decimal("2.00"),
        sku="MILK-001",
    )


@pytest.fixture
def nfc_tag(db, product):
    return NFCTag.objects.create(
        assigned_product=product,
        basket_id="BASKET-001",
        is_active=True,
    )


@pytest.fixture
def auth_client(client, user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {refresh.access_token}"
    return client
