import logging
import uuid

from django.db import transaction
from django.db.models import F

from apps.users.models import User

from .models import TransactionStatus
from .repositories import TransactionRepository

logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()

    def create_checkout_transaction(
        self, user, product, quantity, unit_price, total_amount, shopping_session=None
    ):
        idempotency_key = f"checkout-{user.id}-{product.id}-{uuid.uuid4()}"

        existing = self.repo.get_by_idempotency_key(idempotency_key)
        if existing:
            return existing

        with transaction.atomic():
            locked_user = User.objects.select_for_update().get(pk=user.pk)

            if locked_user.wallet_balance < total_amount:
                raise ValueError(
                    f"Insufficient wallet balance. Required: {total_amount}, "
                    f"Available: {locked_user.wallet_balance}"
                )

            locked_user.wallet_balance = F("wallet_balance") - total_amount
            locked_user.save(update_fields=["wallet_balance"])
            locked_user.refresh_from_db()

            txn = self.repo.create(
                user=locked_user,
                product=product,
                shopping_session=shopping_session,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=total_amount,
                transaction_status=TransactionStatus.COMPLETED,
                idempotency_key=idempotency_key,
            )

        logger.info(
            "Transaction %s completed for user %s: amount=%s",
            txn.id,
            user.id,
            total_amount,
        )
        return txn
