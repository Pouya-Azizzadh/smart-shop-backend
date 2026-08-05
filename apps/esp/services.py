import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

logger = logging.getLogger(__name__)


class ESPCommunicationService:
    """Service layer for ESP device communication."""

    _connected_sessions = {}

    def connect_session(self, session):
        self._connected_sessions[session.id] = {
            "session_id": session.id,
            "tag_uuid": str(session.nfc_tag.uuid),
            "basket_id": session.nfc_tag.basket_id,
            "connected_at": timezone.now(),
        }
        logger.info("ESP session connected: %s", session.id)
        return self._connected_sessions[session.id]

    def disconnect_session(self, session):
        removed = self._connected_sessions.pop(session.id, None)
        if removed:
            logger.info("ESP session disconnected: %s", session.id)
        return removed

    def is_session_connected(self, session_id):
        return session_id in self._connected_sessions

    def validate_event_payload(self, payload):
        required_fields = ("session_id", "tag_uuid", "quantity")
        missing = [field for field in required_fields if field not in payload]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        try:
            session_id = int(payload["session_id"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid session_id") from exc

        try:
            quantity = int(payload["quantity"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid quantity") from exc

        tag_uuid = str(payload["tag_uuid"])
        timestamp = payload.get("timestamp")

        if timestamp:
            if isinstance(timestamp, datetime):
                parsed = timestamp
            else:
                parsed = parse_datetime(str(timestamp))
            if parsed is None:
                raise ValueError("Invalid timestamp format. Use ISO 8601.")
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
        else:
            parsed = timezone.now()

        return {
            "session_id": session_id,
            "tag_uuid": tag_uuid,
            "quantity": quantity,
            "timestamp": parsed,
        }

    def process_event(self, payload):
        validated = self.validate_event_payload(payload)
        from apps.shopping.services import ShoppingSessionService

        return ShoppingSessionService().process_esp_event(
            session_id=validated["session_id"],
            tag_uuid=validated["tag_uuid"],
            quantity=validated["quantity"],
            timestamp=validated["timestamp"],
        )

    def handle_device_disconnect(self, session_id):
        from apps.shopping.repositories import ShoppingSessionRepository

        session = ShoppingSessionRepository.get_active_by_id(session_id)
        if session:
            ShoppingSessionRepository.mark_esp_disconnected(session)
            from apps.shopping.services import ShoppingSessionService

            ShoppingSessionService()._broadcast_session_update(
                session, event_type="esp.disconnected"
            )
            logger.warning("ESP device disconnected for session %s", session_id)
