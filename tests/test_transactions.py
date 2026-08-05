from decimal import Decimal

import pytest

from apps.transactions.services import TransactionService
from apps.users.models import User


@pytest.mark.django_db
class TestTransactionService:
    def test_deducts_wallet_on_checkout(self, product):
        user = User.objects.create_user(
            username="walletuser",
            email="wallet@example.com",
            password="testpass123",
            wallet_balance=Decimal("50.00"),
        )

        txn = TransactionService().create_checkout_transaction(
            user=user,
            product=product,
            quantity=2,
            unit_price=product.price,
            total_amount=Decimal("4.00"),
        )

        user.refresh_from_db()
        assert user.wallet_balance == Decimal("46.00")
        assert txn.transaction_status == "completed"

    def test_rejects_insufficient_balance(self, product):
        user = User.objects.create_user(
            username="pooruser",
            email="poor@example.com",
            password="testpass123",
            wallet_balance=Decimal("1.00"),
        )

        with pytest.raises(ValueError, match="Insufficient wallet balance"):
            TransactionService().create_checkout_transaction(
                user=user,
                product=product,
                quantity=5,
                unit_price=product.price,
                total_amount=Decimal("10.00"),
            )
