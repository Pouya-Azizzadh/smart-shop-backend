import json
import logging
import threading

import paho.mqtt.client as mqtt
from django.conf import settings

logger = logging.getLogger(__name__)

_mqtt_started = False
_mqtt_lock = threading.Lock()


def _on_mqtt_message(client, userdata, msg):
    from apps.esp.services import ESPCommunicationService

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        ESPCommunicationService().process_event(payload)
    except Exception:
        logger.exception("Failed to process MQTT ESP event")


def start_mqtt_listener():
    global _mqtt_started

    if not settings.ESP_MQTT_ENABLED:
        return

    with _mqtt_lock:
        if _mqtt_started:
            return

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_message = _on_mqtt_message

        try:
            client.connect(settings.ESP_MQTT_BROKER, settings.ESP_MQTT_PORT, 60)
            client.subscribe(settings.ESP_MQTT_TOPIC)
            client.loop_start()
            _mqtt_started = True
            logger.info(
                "MQTT listener started on %s:%s topic=%s",
                settings.ESP_MQTT_BROKER,
                settings.ESP_MQTT_PORT,
                settings.ESP_MQTT_TOPIC,
            )
        except Exception:
            logger.exception("Failed to start MQTT listener")
