import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from apps.esp.services import ESPCommunicationService
from apps.nfc.repositories import NFCTagRepository
from apps.transactions.services import TransactionService

from .models import SessionStatus
from .repositories import ShoppingSessionRepository

logger = logging.getLogger(__name__)


class ShoppingSessionService:
    def __init__(self):
        self.session_repo = ShoppingSessionRepository()
        self.nfc_repo = NFCTagRepository()
        self.esp_service = ESPCommunicationService()

    def start_session(self, user, tag_uuid):
        if not user.is_active_account:
            raise ValueError("User account is not active.")

        existing = self.session_repo.get_active_for_user(user)
        if existing:
            raise ValueError("User already has an active shopping session.")

        nfc_tag = self.nfc_repo.get_active_by_uuid(tag_uuid)
        if not nfc_tag:
            raise ValueError("NFC tag not found or inactive.")

        with transaction.atomic():
            session = self.session_repo.create_session(user, nfc_tag)
            self.esp_service.connect_session(session)

        logger.info(
            "Started shopping session %s for user %s with tag %s",
            session.id,
            user.username,
            tag_uuid,
        )
        self._broadcast_session_update(session)
        return session

    def process_esp_event(self, session_id, tag_uuid, quantity, timestamp=None):
        session = self.session_repo.get_active_by_id(session_id)
        if not session:
            raise ValueError("Active shopping session not found.")

        if str(session.nfc_tag.uuid) != str(tag_uuid):
            raise ValueError("NFC tag UUID does not match session.")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        with transaction.atomic():
            session = self.session_repo.update_quantity(session, quantity)

        logger.info(
            "ESP event processed for session %s: quantity=%s",
            session_id,
            quantity,
        )
        self._broadcast_session_update(session)
        return session

    def checkout(self, user):
        session = self.session_repo.get_active_for_user(user)
        if not session:
            raise ValueError("No active shopping session found.")

        if session.checkout_locked:
            raise ValueError("Checkout already in progress.")

        if not session.is_esp_connected():
            logger.warning("ESP device disconnected for session %s", session.id)
            self.session_repo.mark_esp_disconnected(session)
            self._broadcast_session_update(session)
            raise ValueError("ESP device is disconnected. Cannot validate quantity.")

        with transaction.atomic():
            session = ShoppingSessionRepository.get_active_for_user(user)
            if not session:
                raise ValueError("No active shopping session found.")

            self.session_repo.lock_for_checkout(session)

            try:
                product = session.product
                quantity = session.current_quantity
                total_amount = session.current_total_price

                if quantity == 0:
                    self.session_repo.close_session(session, SessionStatus.COMPLETED)
                    self.esp_service.disconnect_session(session)
                    return {
                        "session_id": session.id,
                        "product": product.name,
                        "quantity": 0,
                        "unit_price": product.price,
                        "current_total": 0,
                        "message": "Session closed with no items.",
                    }

                txn = TransactionService().create_checkout_transaction(
                    user=user,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                    total_amount=total_amount,
                    shopping_session=session,
                )

                self.session_repo.close_session(session, SessionStatus.COMPLETED)
                self.esp_service.disconnect_session(session)

            except Exception:
                self.session_repo.unlock_checkout(session)
                raise

        result = {
            "session_id": session.id,
            "product": product.name,
            "quantity": quantity,
            "unit_price": product.price,
            "current_total": total_amount,
            "transaction_id": txn.id,
            "transaction_status": txn.transaction_status,
        }
        self._broadcast_session_update(session, event_type="session.completed")
        logger.info("Checkout completed for session %s", session.id)
        return result

    def get_active_session(self, user):
        return self.session_repo.get_active_for_user(user)

    def _broadcast_session_update(self, session, event_type="session.updated"):
        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        payload = {
            "type": "session_update",
            "event_type": event_type,
            "data": {
                "session_id": session.id,
                "product": session.product.name,
                "quantity": session.current_quantity,
                "unit_price": str(session.unit_price),
                "current_total": str(session.current_total_price),
                "status": session.status,
                "esp_connected": session.is_esp_connected(),
            },
        }

        group_name = f"session_{session.id}"
        async_to_sync(channel_layer.group_send)(group_name, payload)

        user_group = f"user_{session.user_id}"
        async_to_sync(channel_layer.group_send)(user_group, payload)
