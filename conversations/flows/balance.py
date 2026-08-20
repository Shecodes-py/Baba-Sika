"""Balance/progress check - read-only, no AI involved."""

from conversations.services import send_message
from pensions.services import get_progress_summary


def handle_balance_check(user, session):
    summary = get_progress_summary(user)
    readiness = summary["retirement_readiness"]
    bank_balance = summary["bank_account_balance"]
    bank_line = f"₦{bank_balance:,.2f}" if bank_balance is not None else "not yet synced"

    pfa_status = {
        "registered": f"Registered ✅ (RSA PIN: {summary['rsa_pin']})",
        "pending": "Registration pending",
        "failed": "Registration retrying",
        "not_registered": "Not set up yet",
    }.get(summary["pfa_registration_status"], "Not set up yet")

    body = (
        "Your BabaSika progress:\n"
        f"Emergency fund: ₦{summary['emergency_fund_balance']:,.2f}\n"
        f"Retirement fund: ₦{summary['retirement_balance']:,.2f}\n"
        f"Savings account balance: {bank_line}\n"
        f"Pension registration: {pfa_status}\n\n"
        f"Retirement readiness: {readiness['label']} ({readiness['score']:.0f}/100)"
    )
    send_message(user=user, session=session, body=body)
