from rest_framework import serializers

from apps.products.serializers import ProductSerializer

from .models import NFCTag


class NFCTagSerializer(serializers.ModelSerializer):
    assigned_product = ProductSerializer(read_only=True)

    class Meta:
        model = NFCTag
        fields = (
            "id",
            "uuid",
            "assigned_product",
            "basket_id",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "uuid", "created_at")
