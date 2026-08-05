from django.conf import settings
from django.db import models

from apps.nfc.models import NFCTag
from apps.users.models import User


class SessionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CHECKOUT_PENDING = "checkout_pending", "Checkout Pending"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    ESP_DISCONNECTED = "esp_disconnected", "ESP Disconnected"


class ShoppingSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_sessions",
    )
    nfc_tag = models.ForeignKey(
        NFCTag,
        on_delete=models.PROTECT,
        related_name="shopping_sessions",
    )
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.ACTIVE,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    current_quantity = models.PositiveIntegerField(default=0)
    current_total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    esp_last_seen_at = models.DateTimeField(null=True, blank=True)
    checkout_locked = models.BooleanField(default=False)

    class Meta:
        db_table = "shopping_sessions"
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status=SessionStatus.ACTIVE),
                name="unique_active_session_per_user",
            ),
        ]

    def __str__(self):
        return f"Session {self.pk} - {self.user.username}"

    @property
    def product(self):
        return self.nfc_tag.assigned_product

    @property
    def unit_price(self):
        return self.product.price

    def recalculate_total(self):
        self.current_total_price = self.current_quantity * self.unit_price
        return self.current_total_price

    def is_esp_connected(self):
        if not self.esp_last_seen_at:
            return False
        timeout = settings.ESP_DEVICE_TIMEOUT_SECONDS
        from django.utils import timezone

        return (timezone.now() - self.esp_last_seen_at).total_seconds() <= timeout
