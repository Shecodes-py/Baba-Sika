import logging

from celery import shared_task
from django.utils import timezone

from .models import MagicLinkStatus, MagicLinkToken

logger = logging.getLogger(__name__)


@shared_task
def expire_magic_links_task():
    stale = MagicLinkToken.objects.filter(
        status=MagicLinkStatus.ISSUED, expires_at__lte=timezone.now()
    )
    count = stale.update(status=MagicLinkStatus.EXPIRED)
    if count:
        logger.info("Expired %d stale MagicLinkToken(s)", count)
    return count
