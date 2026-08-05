from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "total_amount",
            "transaction_status",
            "created_at",
        )
        read_only_fields = fields
