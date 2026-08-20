"""
IDLE state: any free-text message. Classified via ai_engine (Gemini/stub) to
route to the right read-only or income-logging flow. Never leads to a bank
call directly - at most it creates a PendingAction (via the income flow ->
pensions.tasks.generate_ai_recommendation_task), same as every other path.
"""

import ai_engine.services as ai_services

from . import balance, dashboard, income


def handle_idle_message(user, session, message_log, raw_body):
    if session.context.get("awaiting_income_amount"):
        income.handle_awaiting_income_amount_reply(user, session, raw_body)
        return

    parsed_output, _ai_log = ai_services.classify_intent(
        user=user, message_text=raw_body, context={"state": session.state}
    )
    intent = parsed_output.get("intent", "unknown")

    if intent == "balance_check":
        balance.handle_balance_check(user, session)
    elif intent == "show_dashboard":
        dashboard.handle_show_dashboard(user, session)
    elif intent == "log_income":
        income.handle_income_intent(user, session, parsed_output.get("entities", {}))
    else:
        _send_help(user, session)


def _send_help(user, session):
    from conversations.services import send_message

    send_message(
        user=user,
        session=session,
        body=(
            "I can help with:\n"
            "- Reply BALANCE to check your savings progress\n"
            "- Reply DASHBOARD for your dashboard link\n"
            "- Tell me when you get paid, e.g. \"I received 5000\""
        ),
    )
