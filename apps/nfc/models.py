import uuid

from django.db import models

from apps.products.models import Product


class NFCTag(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    assigned_product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="nfc_tags",
    )
    basket_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "nfc_tags"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.basket_id} ({self.uuid})"
