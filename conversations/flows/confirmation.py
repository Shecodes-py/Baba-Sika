"""
AWAITING_CONFIRMATION (approve/adjust/skip numbered reply) and AWAITING_PIN
(PIN re-entry) - the only two states that can lead to money moving, and
only ever through pensions.services.confirm_and_execute_pending_action.
"""

import logging
from decimal import Decimal, InvalidOperation

from conversations.models import ConversationState
from conversations.services import send_message, set_session_state
from pensions.models import ContributionDestination, PendingAction, PendingActionStatus
from pensions.services import (
    PendingActionNotActionableError,
    PinIncorrectError,
    PinLockedError,
    decline_pending_action,
    confirm_and_execute_pending_action,
    get_progress_summary,
)

logger = logging.getLogger(__name__)

PIN_LOCKOUT_MINUTES = 30  # kept in sync with accounts.models.PIN_LOCKOUT_MINUTES for messaging


def build_recommendation_menu_text(pending_action: PendingAction) -> str:
    copy = pending_action.proposed_payload.get("whatsapp_copy") or (
        f"BabaSika suggests contributing ₦{pending_action.proposed_payload.get('suggested_amount')} today."
    )
    return f"{copy}\n\n1. Approve\n2. Adjust amount\n3. Skip"


def _get_actionable_pending_action(user, session):
    pending_action_id = session.context.get("pending_action_id")
    if not pending_action_id:
        return None
    return PendingAction.objects.filter(pk=pending_action_id, user=user).first()


def handle_confirmation_reply(user, session, message_log, raw_body):
    pending_action = _get_actionable_pending_action(user, session)
    if not pending_action or pending_action.status != PendingActionStatus.PENDING or pending_action.is_expired:
        send_message(user=user, session=session, body="That offer is no longer available.")
        set_session_state(session, ConversationState.IDLE, context={})
        return

    reply = raw_body.strip().lower()

    if session.context.get("adjusting"):
        _handle_adjust_amount_reply(user, session, pending_action, reply)
        return

    if reply in {"1", "approve"}:
        send_message(
            user=user,
            session=session,
            body="Reply with your 4-digit PIN to confirm this contribution.",
        )
        set_session_state(session, ConversationState.AWAITING_PIN, context=session.context)
        return

    if reply in {"2", "adjust"}:
        send_message(
            user=user,
            session=session,
            body="Reply with the amount (numbers only) you'd like to contribute instead.",
        )
        set_session_state(
            session,
            ConversationState.AWAITING_CONFIRMATION,
            context={**session.context, "adjusting": True},
        )
        return

    if reply in {"3", "skip"}:
        decline_pending_action(pending_action, reason="user_skipped")
        send_message(user=user, session=session, body="No problem, skipped for now.")
        set_session_state(session, ConversationState.IDLE, context={})
        return

    send_message(user=user, session=session, body="Sorry, reply 1 to Approve, 2 to Adjust, or 3 to Skip.")


def _handle_adjust_amount_reply(user, session, pending_action, reply):
    try:
        amount = Decimal(reply.replace(",", "").replace("₦", "").strip())
        if amount <= 0:
            raise InvalidOperation
    except InvalidOperation:
        send_message(user=user, session=session, body="Please reply with a valid amount, numbers only, e.g. 1500.")
        return

    pending_action.proposed_payload["suggested_amount"] = str(amount)
    pending_action.save(update_fields=["proposed_payload", "updated_at"])

    context = {**session.context}
    context.pop("adjusting", None)
    body = (
        f"Updated: BabaSika will set aside ₦{amount:,.2f}.\n\n1. Approve\n2. Adjust amount\n3. Skip"
    )
    send_message(user=user, session=session, body=body)
    set_session_state(session, ConversationState.AWAITING_CONFIRMATION, context=context)


def handle_pin_reply(user, session, message_log, raw_body):
    pending_action = _get_actionable_pending_action(user, session)
    if not pending_action:
        send_message(user=user, session=session, body="That offer is no longer available.")
        set_session_state(session, ConversationState.IDLE, context={})
        return

    raw_pin = raw_body.strip()
    try:
        confirm_and_execute_pending_action(
            pending_action, raw_pin=raw_pin, message_sid=message_log.twilio_message_sid or ""
        )
    except PinLockedError:
        send_message(
            user=user,
            session=session,
            body=f"Your PIN is locked for {PIN_LOCKOUT_MINUTES} minutes after too many wrong tries. Try again later.",
        )
        # Stay in AWAITING_PIN: once the lockout window passes, the same
        # reply flow will work again for this pending action (if it hasn't
        # since expired - handled by the PendingActionNotActionableError path).
        return
    except PinIncorrectError:
        user.refresh_from_db(fields=["pin_attempt_count"])
        from accounts.models import PIN_MAX_ATTEMPTS

        remaining = max(PIN_MAX_ATTEMPTS - user.pin_attempt_count, 0)
        send_message(user=user, session=session, body=f"Incorrect PIN. {remaining} attempt(s) left.")
        return
    except PendingActionNotActionableError:
        send_message(user=user, session=session, body="That offer has expired or is no longer available.")
        set_session_state(session, ConversationState.IDLE, context={})
        return

    pending_action.refresh_from_db()
    emergency = pending_action.contributions.filter(destination=ContributionDestination.EMERGENCY_FUND).first()
    retirement = pending_action.contributions.filter(destination=ContributionDestination.RETIREMENT_FUND).first()
    summary = get_progress_summary(user)
    body = (
        "Done! ✅ Transfer successful.\n"
        f"₦{emergency.amount:,.2f} → Emergency fund\n"
        f"₦{retirement.amount:,.2f} → Retirement fund\n\n"
        "📊 Updated balances:\n"
        f"Emergency: ₦{summary['emergency_fund_balance']:,.2f}\n"
        f"Retirement: ₦{summary['retirement_balance']:,.2f}\n\n"
        "Reply BALANCE anytime to check your progress."
    )
    send_message(user=user, session=session, body=body)
    set_session_state(session, ConversationState.IDLE, context={})
