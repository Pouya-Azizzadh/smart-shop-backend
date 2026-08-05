from django.utils import timezone

from .models import SessionStatus, ShoppingSession


class ShoppingSessionRepository:
    @staticmethod
    def get_active_for_user(user):
        return (
            ShoppingSession.objects.select_related(
                "nfc_tag__assigned_product",
                "user",
            )
            .filter(user=user, status=SessionStatus.ACTIVE)
            .first()
        )

    @staticmethod
    def get_by_id(session_id):
        return (
            ShoppingSession.objects.select_related(
                "nfc_tag__assigned_product",
                "user",
            )
            .filter(pk=session_id)
            .first()
        )

    @staticmethod
    def get_active_by_id(session_id):
        return (
            ShoppingSession.objects.select_related(
                "nfc_tag__assigned_product",
                "user",
            )
            .filter(pk=session_id, status=SessionStatus.ACTIVE)
            .first()
        )

    @staticmethod
    def create_session(user, nfc_tag):
        return ShoppingSession.objects.create(user=user, nfc_tag=nfc_tag)

    @staticmethod
    def update_quantity(session, quantity):
        session.current_quantity = quantity
        session.recalculate_total()
        session.esp_last_seen_at = timezone.now()
        session.save(
            update_fields=[
                "current_quantity",
                "current_total_price",
                "esp_last_seen_at",
            ]
        )
        return session

    @staticmethod
    def mark_esp_disconnected(session):
        session.status = SessionStatus.ESP_DISCONNECTED
        session.save(update_fields=["status"])
        return session

    @staticmethod
    def close_session(session, status=SessionStatus.COMPLETED):
        session.status = status
        session.ended_at = timezone.now()
        session.save(update_fields=["status", "ended_at"])
        return session

    @staticmethod
    def lock_for_checkout(session):
        session.checkout_locked = True
        session.status = SessionStatus.CHECKOUT_PENDING
        session.save(update_fields=["checkout_locked", "status"])
        return session

    @staticmethod
    def unlock_checkout(session):
        session.checkout_locked = False
        session.status = SessionStatus.ACTIVE
        session.save(update_fields=["checkout_locked", "status"])
        return session
