import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from . import services

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def sync_bank_balance_task(self, user_id):
    try:
        services.sync_balance(User.objects.get(pk=user_id))
    except Exception as exc:  # noqa: BLE001 - retry on any transient provider error
        logger.warning("sync_bank_balance_task failed for user=%s: %s", user_id, exc)
        raise self.retry(exc=exc)
