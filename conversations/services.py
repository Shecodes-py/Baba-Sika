"""
Session/message plumbing shared by the webhook view and the flow handlers.
Flow-specific logic (what to say/do at each state) lives in conversations/flows/.
"""

import logging

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import ConversationSession, ConversationState, MessageDirection, MessageLog, MessageType
from .whatsapp_client import send_whatsapp_text

logger = logging.getLogger(__name__)

User = get_user_model()

# States during which the next inbound message is a raw transaction PIN and
# must never be persisted verbatim in the audit log.
PIN_AWAITING_STATES = {ConversationState.AWAITING_PIN, ConversationState.ONBOARDING_PIN_SETUP}


def get_or_create_user(phone_number: str) -> User:
    phone_number = User.objects.normalize_phone(phone_number)
    user, _ = User.objects.get_or_create(phone_number=phone_number)
    return user


def get_or_create_session(user) -> ConversationSession:
    session, _ = ConversationSession.objects.get_or_create(user=user)
    return session


def log_inbound_message(*, user, session, twilio_message_sid, body, raw_payload, message_type=MessageType.TEXT):
    """
    Idempotent on twilio_message_sid. Returns (message_log, created) -
    callers must skip processing entirely when created is False (Twilio
    retried a delivery we already handled).
    """
    redact = session.state in PIN_AWAITING_STATES
    message_log, created = MessageLog.objects.get_or_create(
        twilio_message_sid=twilio_message_sid,
        defaults={
            "user": user,
            "session": session,
            "direction": MessageDirection.INBOUND,
            "body": "[redacted - transaction PIN]" if redact else body,
            "message_type": message_type,
            "raw_payload": {"redacted": True} if redact else raw_payload,
        },
    )
    return message_log, created


def mark_processed(message_log: MessageLog):
    message_log.processed = True
    message_log.processed_at = timezone.now()
    message_log.save(update_fields=["processed", "processed_at", "updated_at"])


def send_message(*, user, session=None, body: str, message_type=MessageType.TEXT) -> MessageLog:
    sid = send_whatsapp_text(to_phone_number=user.phone_number, body=body)
    return MessageLog.objects.create(
        user=user,
        session=session,
        direction=MessageDirection.OUTBOUND,
        twilio_message_sid=sid or None,
        body=body,
        message_type=message_type,
    )


def set_session_state(session: ConversationSession, state: str, *, context: dict | None = None):
    session.state = state
    if context is not None:
        session.context = context
    session.save(update_fields=["state", "context", "updated_at"])
    return session


# --- messages triggered from other apps (kept here so pensions/account_provisioning
# never need to know WhatsApp copy formatting) ---------------------------

def send_contribution_recommendation_message(*, user, pending_action):
    from .flows.confirmation import build_recommendation_menu_text

    session = get_or_create_session(user)
    body = build_recommendation_menu_text(pending_action)
    send_message(user=user, session=session, body=body)
    set_session_state(
        session,
        ConversationState.AWAITING_CONFIRMATION,
        context={"pending_action_id": str(pending_action.pk)},
    )
