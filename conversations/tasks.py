import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from accounts.models import OnboardingState
from pensions.models import ContributionSchedule

from .models import ConversationState
from .services import get_or_create_session, send_message

logger = logging.getLogger(__name__)

User = get_user_model()

NUDGE_BODY = (
    "\U0001F44B Just checking in - have you been paid recently? Reply with the amount "
    "(e.g. \"5000\") and I'll suggest how much to set aside for your future."
)


@shared_task
def send_savings_nudges_task():
    """
    Scheduled savings nudge, run by Celery beat on ContributionSchedule's
    cadence. Only nudges users who are fully onboarded and not already mid
    conversation (IDLE), so it never talks over an active flow.
    """
    schedules = ContributionSchedule.objects.filter(is_active=True).select_related("plan__user")
    sent = 0
    for schedule in schedules:
        user = schedule.plan.user
        if user.onboarding_state != OnboardingState.COMPLETED:
            continue
        session = get_or_create_session(user)
        if session.state != ConversationState.IDLE:
            continue
        send_message(user=user, session=session, body=NUDGE_BODY)
        sent += 1
    if sent:
        logger.info("Sent %d savings nudge(s)", sent)
    return sent
