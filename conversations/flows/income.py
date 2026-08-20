"""
User-initiated 'I got paid' flow. There is no live bank integration to push
income events to us yet, so this manual entry is the only way income
patterns reach the AI recommendation step for now - see
account_provisioning.providers for why.
"""

import uuid
from decimal import Decimal, InvalidOperation

from django.utils import timezone

from account_provisioning.models import BankTransactionMirror, TransactionDirection
from conversations.services import send_message, set_session_state
from pensions.tasks import generate_ai_recommendation_task


def handle_income_intent(user, session, entities: dict):
    amount = entities.get("amount") if entities else None
    if amount:
        _log_income_and_recommend(user, session, amount)
        return
    send_message(user=user, session=session, body="How much did you receive? Reply with the amount, e.g. 5000.")
    set_session_state(session, session.state, context={**session.context, "awaiting_income_amount": True})


def handle_awaiting_income_amount_reply(user, session, raw_body):
    _log_income_and_recommend(user, session, raw_body.strip())


def _log_income_and_recommend(user, session, raw_amount):
    try:
        amount = Decimal(str(raw_amount).replace(",", "").replace("₦", "").strip())
        if amount <= 0:
            raise InvalidOperation
    except InvalidOperation:
        send_message(user=user, session=session, body="Please reply with a valid amount, numbers only, e.g. 5000.")
        return

    BankTransactionMirror.objects.create(
        user=user,
        transaction_ref=f"manual-{uuid.uuid4().hex}",
        amount=amount,
        direction=TransactionDirection.CREDIT,
        narration="Manually logged income (WhatsApp)",
        occurred_at=timezone.now(),
        raw_payload={"source": "whatsapp_manual_entry"},
    )
    context = {**session.context}
    context.pop("awaiting_income_amount", None)
    set_session_state(session, session.state, context=context)

    send_message(user=user, session=session, body="Got it, thinking about how much to set aside...")
    generate_ai_recommendation_task.delay(
        user_id=str(user.pk), income_event={"amount": str(amount), "source": "manual"}
    )
