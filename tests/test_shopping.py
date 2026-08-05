from decimal import Decimal

import pytest
from django.urls import reverse

from apps.shopping.models import SessionStatus, ShoppingSession
from apps.transactions.models import Transaction


@pytest.mark.django_db
class TestStartShopping:
    def test_start_session_success(self, auth_client, user, nfc_tag):
        url = reverse("shopping-start")
        response = auth_client.post(url, {"tag_uuid": str(nfc_tag.uuid)}, format="json")

        assert response.status_code == 201
        assert response.data["product"] == "Milk"
        assert response.data["status"] == SessionStatus.ACTIVE
        assert ShoppingSession.objects.filter(user=user, status=SessionStatus.ACTIVE).exists()

    def test_start_session_invalid_tag(self, auth_client):
        url = reverse("shopping-start")
        response = auth_client.post(
            url,
            {"tag_uuid": "00000000-0000-0000-0000-000000000000"},
            format="json",
        )

        assert response.status_code == 400

    def test_start_session_requires_auth(self, client, nfc_tag):
        url = reverse("shopping-start")
        response = client.post(url, {"tag_uuid": str(nfc_tag.uuid)}, format="json")

        assert response.status_code == 401


@pytest.mark.django_db
class TestCheckout:
    def test_checkout_success(self, auth_client, user, nfc_tag, settings):
        settings.ESP_DEVICE_TIMEOUT_SECONDS = 300

        start_url = reverse("shopping-start")
        auth_client.post(start_url, {"tag_uuid": str(nfc_tag.uuid)}, format="json")

        session = ShoppingSession.objects.get(user=user)
        session.current_quantity = 3
        session.recalculate_total()
        from django.utils import timezone

        session.esp_last_seen_at = timezone.now()
        session.save()

        checkout_url = reverse("shopping-checkout")
        response = auth_client.post(checkout_url)

        assert response.status_code == 200
        assert response.data["quantity"] == 3
        assert Decimal(str(response.data["current_total"])) == Decimal("6.00")

        user.refresh_from_db()
        assert user.wallet_balance == Decimal("94.00")
        assert Transaction.objects.filter(user=user).count() == 1

    def test_checkout_insufficient_balance(self, auth_client, user, nfc_tag, settings):
        settings.ESP_DEVICE_TIMEOUT_SECONDS = 300
        user.wallet_balance = Decimal("1.00")
        user.save()

        start_url = reverse("shopping-start")
        auth_client.post(start_url, {"tag_uuid": str(nfc_tag.uuid)}, format="json")

        session = ShoppingSession.objects.get(user=user)
        session.current_quantity = 3
        session.recalculate_total()
        from django.utils import timezone

        session.esp_last_seen_at = timezone.now()
        session.save()

        checkout_url = reverse("shopping-checkout")
        response = auth_client.post(checkout_url)

        assert response.status_code == 402


@pytest.mark.django_db
class TestESPEvents:
    def test_esp_event_updates_session(self, auth_client, user, nfc_tag, settings):
        settings.ESP_DEVICE_API_KEY = "test-esp-key"

        start_url = reverse("shopping-start")
        auth_client.post(start_url, {"tag_uuid": str(nfc_tag.uuid)}, format="json")

        session = ShoppingSession.objects.get(user=user)
        esp_url = reverse("esp-events")

        client = auth_client
        client.defaults["HTTP_X_ESP_API_KEY"] = "test-esp-key"

        response = client.post(
            esp_url,
            {
                "session_id": session.id,
                "tag_uuid": str(nfc_tag.uuid),
                "quantity": 3,
                "timestamp": "2026-01-01T10:00:00Z",
            },
            format="json",
        )

        assert response.status_code == 200
        assert response.data["quantity"] == 3
        assert Decimal(str(response.data["current_total"])) == Decimal("6.00")

        session.refresh_from_db()
        assert session.current_quantity == 3

    def test_esp_event_invalid_api_key(self, auth_client, user, nfc_tag):
        start_url = reverse("shopping-start")
        auth_client.post(start_url, {"tag_uuid": str(nfc_tag.uuid)}, format="json")

        session = ShoppingSession.objects.get(user=user)
        esp_url = reverse("esp-events")

        response = auth_client.post(
            esp_url,
            {
                "session_id": session.id,
                "tag_uuid": str(nfc_tag.uuid),
                "quantity": 1,
            },
            format="json",
        )

        assert response.status_code == 403
