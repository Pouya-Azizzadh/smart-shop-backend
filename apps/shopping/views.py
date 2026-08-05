import logging

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CheckoutResponseSerializer,
    ShoppingSessionSerializer,
    StartShoppingSerializer,
)
from .services import ShoppingSessionService

logger = logging.getLogger(__name__)


class StartShoppingView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        request=StartShoppingSerializer,
        responses={201: ShoppingSessionSerializer},
        summary="Start a shopping session from NFC scan",
    )
    def post(self, request):
        serializer = StartShoppingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            session = ShoppingSessionService().start_session(
                user=request.user,
                tag_uuid=serializer.validated_data["tag_uuid"],
            )
        except ValueError as exc:
            logger.warning("Failed to start session: %s", exc)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ShoppingSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )


class CheckoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        responses={200: CheckoutResponseSerializer},
        summary="Checkout active shopping session",
    )
    def post(self, request):
        try:
            result = ShoppingSessionService().checkout(user=request.user)
        except ValueError as exc:
            logger.warning("Checkout failed for user %s: %s", request.user.id, exc)
            if "Insufficient wallet balance" in str(exc):
                return Response({"detail": str(exc)}, status=status.HTTP_402_PAYMENT_REQUIRED)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            logger.exception("Checkout error for user %s", request.user.id)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)


class ActiveSessionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        responses={200: ShoppingSessionSerializer},
        summary="Get active shopping session",
    )
    def get(self, request):
        session = ShoppingSessionService().get_active_session(request.user)
        if not session:
            return Response({"detail": "No active session."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ShoppingSessionSerializer(session).data)
