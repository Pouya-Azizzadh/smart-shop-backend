import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ShoppingSession

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ShoppingSession)
def log_session_changes(sender, instance, created, **kwargs):
    if created:
        logger.info("ShoppingSession %s created for user %s", instance.id, instance.user_id)
