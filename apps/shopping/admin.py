from django.contrib import admin

from .models import ShoppingSession


@admin.register(ShoppingSession)
class ShoppingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "nfc_tag",
        "status",
        "current_quantity",
        "current_total_price",
        "started_at",
    )
    list_filter = ("status",)
    search_fields = ("user__username", "nfc_tag__basket_id")
