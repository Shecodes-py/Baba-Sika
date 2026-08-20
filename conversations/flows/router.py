"""
Single dispatch point: session.state -> handler. Called synchronously from
the Twilio webhook view (see conversations.views) - deliberately NOT put
behind Celery, so a transaction PIN never has to transit the message broker
(see conversations.services.PIN_AWAITING_STATES for the corresponding
audit-log redaction).
"""

import logging

from conversations.models import ConversationState
from conversations.services import send_message

from . import confirmation, idle, onboarding

logger = logging.getLogger(__name__)

_HANDLERS = {
    ConversationState.ONBOARDING_GREETING: onboarding.handle_greeting,
    ConversationState.ONBOARDING_OCCUPATION: onboarding.handle_occupation_reply,
    ConversationState.ONBOARDING_BANK_LINK: onboarding.handle_bank_link_retry,
    ConversationState.ONBOARDING_PFA_SELECTION: onboarding.handle_pfa_selection_reply,
    ConversationState.ONBOARDING_CONSENT: onboarding.handle_consent_reply,
    ConversationState.ONBOARDING_PIN_SETUP: onboarding.handle_pin_setup_reply,
    ConversationState.AWAITING_CONFIRMATION: confirmation.handle_confirmation_reply,
    ConversationState.AWAITING_PIN: confirmation.handle_pin_reply,
}


def dispatch(*, user, session, message_log, raw_body: str):
    handler = _HANDLERS.get(session.state)
    try:
        if handler is not None:
            handler(user, session, message_log, raw_body)
        else:
            # IDLE and EXPIRED both fall through to free-text/AI-intent handling.
            idle.handle_idle_message(user, session, message_log, raw_body)
    except Exception:
        logger.exception("Unhandled error dispatching message for user=%s state=%s", user.pk, session.state)
        send_message(
            user=user,
            session=session,
            body="Sorry, something went wrong on our end. Please try again in a moment.",
        )
