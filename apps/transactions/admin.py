from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "quantity",
        "total_amount",
        "transaction_status",
        "created_at",
    )
    list_filter = ("transaction_status",)
    search_fields = ("user__username", "product__name")
