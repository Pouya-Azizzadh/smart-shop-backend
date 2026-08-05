from rest_framework import serializers


class ESPEventSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    tag_uuid = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=0)
    timestamp = serializers.DateTimeField(required=False)


class ESPEventResponseSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    product = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_total = serializers.DecimalField(max_digits=12, decimal_places=2)
