from django.db import models

from apps.products.models import Product
from apps.shopping.models import ShoppingSession
from apps.users.models import User


class TransactionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class Transaction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    shopping_session = models.ForeignKey(
        ShoppingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    idempotency_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transaction {self.pk} - {self.user.username}"
