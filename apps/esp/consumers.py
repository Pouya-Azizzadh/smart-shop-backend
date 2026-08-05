import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class ShoppingSessionConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for mobile app real-time session updates."""

    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return

        self.session_id = self.scope["url_route"]["kwargs"].get("session_id")
        self.user_group = f"user_{self.user.id}"
        self.session_group = (
            f"session_{self.session_id}" if self.session_id is not None else None
        )

        await self.channel_layer.group_add(self.user_group, self.channel_name)
        if self.session_group:
            await self.channel_layer.group_add(self.session_group, self.channel_name)

        await self.accept()
        logger.info(
            "WebSocket connected: user=%s session=%s",
            self.user.id,
            self.session_id,
        )

    async def disconnect(self, close_code):
        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if hasattr(self, "session_group") and self.session_group:
            await self.channel_layer.group_discard(self.session_group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        await self.send_json({"type": "ack", "received": content})

    async def session_update(self, event):
        await self.send_json(
            {
                "type": event.get("event_type", "session.updated"),
                "data": event["data"],
            }
        )


class ESPDeviceConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for ESP device real-time events."""

    async def connect(self):
        headers = dict(self.scope.get("headers", []))
        api_key = headers.get(b"x-esp-api-key", b"").decode()

        from django.conf import settings

        if api_key != settings.ESP_DEVICE_API_KEY:
            await self.close(code=4003)
            return

        await self.accept()
        logger.info("ESP device WebSocket connected")

    async def disconnect(self, close_code):
        pass

    async def receive_json(self, content, **kwargs):
        from channels.db import database_sync_to_async
        from apps.esp.services import ESPCommunicationService

        try:
            session = await database_sync_to_async(
                ESPCommunicationService().process_event
            )(content)
            await self.send_json(
                {
                    "type": "event.ack",
                    "session_id": session.id,
                    "quantity": session.current_quantity,
                    "current_total": str(session.current_total_price),
                }
            )
        except ValueError as exc:
            await self.send_json({"type": "error", "detail": str(exc)})
        except Exception as exc:
            logger.exception("ESP WebSocket event processing failed")
            await self.send_json({"type": "error", "detail": "Internal server error"})
