from rest_framework import serializers

from .models import ShoppingSession


class StartShoppingSerializer(serializers.Serializer):
    tag_uuid = serializers.UUIDField()


class ShoppingSessionSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name", read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    esp_connected = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingSession
        fields = (
            "id",
            "product",
            "status",
            "started_at",
            "ended_at",
            "current_quantity",
            "current_total_price",
            "unit_price",
            "esp_connected",
        )

    def get_esp_connected(self, obj):
        return obj.is_esp_connected()


class SessionUpdateResponseSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    product = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_total = serializers.DecimalField(max_digits=12, decimal_places=2)


class CheckoutResponseSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    product = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = serializers.IntegerField(required=False)
    transaction_status = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
