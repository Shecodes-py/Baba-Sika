import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from . import services

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task
def expire_pending_actions_task():
    count = services.expire_stale_pending_actions()
    if count:
        logger.info("Expired %d stale PendingAction(s)", count)
    return count


@shared_task
def retry_pfa_registrations_task():
    """
    Periodic best-effort retry for plans stuck PENDING/FAILED with the mock
    PFA (simulating PenCom not having issued a PIN yet, or a transient
    outage). Never touches plans that are already REGISTERED or that never
    opted into a PFA (preferred_pfa blank).
    """
    from .models import PensionPlan, PFARegistrationStatus

    plans = PensionPlan.objects.filter(
        pfa_registration_status__in=[PFARegistrationStatus.PENDING, PFARegistrationStatus.FAILED]
    ).exclude(preferred_pfa="")
    retried = 0
    for plan in plans:
        services.register_with_pfa(plan.user)
        retried += 1
    if retried:
        logger.info("Retried PFA registration for %d plan(s)", retried)
    return retried


@shared_task(bind=True, max_retries=3, default_retry_delay=15)
def generate_ai_recommendation_task(self, *, user_id: str, income_event: dict):
    """
    Triggered on an income event (Wema webhook credit, or a user manually
    logging income via WhatsApp). Calls the AI layer for a draft
    recommendation, writes the PendingAction, then hands off to
    conversations to actually send the numbered-menu WhatsApp message -
    this task itself never sends anything or moves money.
    """
    import ai_engine.services as ai_services
    from conversations.services import send_contribution_recommendation_message

    try:
        user = User.objects.get(pk=user_id)
        parsed_output, ai_log = ai_services.generate_recommendation(
            user=user, income_context=income_event
        )
        pending_action = services.create_pending_action_from_recommendation(
            user=user,
            parsed_output=parsed_output,
            ai_log=ai_log,
            source_context=income_event,
        )
        send_contribution_recommendation_message(user=user, pending_action=pending_action)
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_ai_recommendation_task failed for user=%s", user_id)
        raise self.retry(exc=exc)
