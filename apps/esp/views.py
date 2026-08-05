import logging

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.esp.permissions import ESPDevicePermission
from apps.esp.serializers import ESPEventSerializer, ESPEventResponseSerializer
from apps.esp.services import ESPCommunicationService

logger = logging.getLogger(__name__)


class ESPEventView(APIView):
    """HTTP endpoint for ESP devices to push quantity events."""

    permission_classes = (ESPDevicePermission,)

    @extend_schema(
        request=ESPEventSerializer,
        responses={200: ESPEventResponseSerializer},
        summary="Receive ESP quantity update event",
    )
    def post(self, request):
        serializer = ESPEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            session = ESPCommunicationService().process_event(
                serializer.validated_data
            )
        except ValueError as exc:
            logger.warning("Invalid ESP event: %s", exc)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "session_id": session.id,
                "product": session.product.name,
                "quantity": session.current_quantity,
                "unit_price": session.unit_price,
                "current_total": session.current_total_price,
            },
            status=status.HTTP_200_OK,
        )
