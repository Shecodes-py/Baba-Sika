"""
Onboarding: greeting -> occupation -> account provisioning -> PFA selection
-> consent -> PIN setup -> done (fires the dashboard magic link).

PFA registration (after consent) and account provisioning (after occupation)
are both best-effort against mocked providers - neither can block onboarding
from completing. See account_provisioning.providers and pensions.providers.
"""

import logging

from django.utils import timezone

from account_provisioning.providers import BankProviderError
from account_provisioning.services import link_account
from accounts.models import ConsentRecord, ConsentType, OccupationType, OnboardingState
from accounts.validators import validate_transaction_pin
from conversations.models import ConversationState
from conversations.services import send_message, set_session_state
from dashboard_bridge.models import MagicLinkRequestSource
from dashboard_bridge.services import issue_magic_link
from pensions.models import PFAChoice, PFARegistrationStatus
from pensions.services import ensure_plan_scaffold, register_with_pfa

logger = logging.getLogger(__name__)

LANGUAGE_MENU_ORDER = [
    ("en", "English"),
    ("pcm", "Pidgin"),
    ("yo", "Yorùbá"),
    ("ha", "Hausa"),
    ("ig", "Igbo"),
]

OCCUPATION_MENU_ORDER = [
    OccupationType.TRADER,
    OccupationType.ARTISAN,
    OccupationType.POS_AGENT,
    OccupationType.TAILOR,
    OccupationType.MECHANIC,
    OccupationType.MARKET_WOMAN,
    OccupationType.OTHER,
]

PFA_MENU_ORDER = list(PFAChoice)

CONSENT_TEXT_VERSION = "v1"

TERMS_SUMMARY = (
    "By continuing you agree to let BabaSika: (a) hold a savings account on "
    "your behalf and read its balance/transactions to suggest pension "
    "contributions, (b) move money out of it ONLY after you approve a "
    "specific amount and confirm with your PIN, and (c) share your basic "
    "details with {pfa} to register your Retirement Savings Account. "
    "Reply 1 to agree."
)


def _language_menu_text() -> str:
    lines = [f"{i}. {label}" for i, (_code, label) in enumerate(LANGUAGE_MENU_ORDER, start=1)]
    return "Please select your preferred language:\n" + "\n".join(lines)


def _occupation_menu_text() -> str:
    lines = [f"{i}. {choice.label}" for i, choice in enumerate(OCCUPATION_MENU_ORDER, start=1)]
    return "What best describes what you do?\n" + "\n".join(lines)


def _pfa_menu_text() -> str:
    lines = [f"{i}. {choice.label}" for i, choice in enumerate(PFA_MENU_ORDER, start=1)]
    return "Which Pension Fund Administrator (PFA) would you like your retirement savings registered with?\n" + "\n".join(lines)


def _looks_like_rsa_pin(value: str) -> bool:
    # No real format spec to validate against (PenCom PIN shape isn't public) -
    # just enough of a sanity check to reject obvious junk before storing it.
    return value.isalnum() and 6 <= len(value) <= 20


def handle_greeting(user, session, message_log, raw_body):
    body = (
        "Welcome to BabaSika \U0001F44B - your AI-guided pension savings companion.\n\n"
        + _language_menu_text()
    )
    send_message(user=user, session=session, body=body)
    set_session_state(session, ConversationState.ONBOARDING_LANGUAGE)


def handle_language_reply(user, session, message_log, raw_body):
    reply = raw_body.strip()
    if not reply.isdigit() or not (1 <= int(reply) <= len(LANGUAGE_MENU_ORDER)):
        send_message(user=user, session=session, body="Please reply with a number from the list.\n\n" + _language_menu_text())
        return

    # Captured for later - not yet wired into WhatsApp copy (still English
    # throughout for this pass), same "headline-only" scope as the dashboard.
    language_code, _label = LANGUAGE_MENU_ORDER[int(reply) - 1]
    user.preferred_language = language_code
    user.save(update_fields=["preferred_language", "updated_at"])

    send_message(user=user, session=session, body=_occupation_menu_text())
    set_session_state(session, ConversationState.ONBOARDING_OCCUPATION)


def handle_occupation_reply(user, session, message_log, raw_body):
    reply = raw_body.strip()
    if not reply.isdigit() or not (1 <= int(reply) <= len(OCCUPATION_MENU_ORDER)):
        send_message(user=user, session=session, body="Please reply with a number from the list.\n\n" + _occupation_menu_text())
        return

    user.occupation_type = OCCUPATION_MENU_ORDER[int(reply) - 1]
    user.onboarding_state = OnboardingState.OCCUPATION_SELECTED
    user.save(update_fields=["occupation_type", "onboarding_state", "updated_at"])
    ensure_plan_scaffold(user)

    _attempt_bank_link(user, session)


def _attempt_bank_link(user, session):
    send_message(user=user, session=session, body="Thanks! Setting up your BabaSika savings account, one moment...")
    try:
        link_account(user)
    except BankProviderError as exc:
        logger.warning("Account provisioning failed during onboarding for user=%s: %s", user.pk, exc)
        send_message(
            user=user,
            session=session,
            body="We couldn't set up your savings account right now. Reply anything to try again.",
        )
        set_session_state(session, ConversationState.ONBOARDING_BANK_LINK)
        return

    user.onboarding_state = OnboardingState.BANK_LINKED
    user.save(update_fields=["onboarding_state", "updated_at"])
    send_message(user=user, session=session, body=_pfa_menu_text())
    set_session_state(session, ConversationState.ONBOARDING_PFA_SELECTION)


def handle_bank_link_retry(user, session, message_log, raw_body):
    _attempt_bank_link(user, session)


def handle_pfa_selection_reply(user, session, message_log, raw_body):
    reply = raw_body.strip()
    if not reply.isdigit() or not (1 <= int(reply) <= len(PFA_MENU_ORDER)):
        send_message(user=user, session=session, body="Please reply with a number from the list.\n\n" + _pfa_menu_text())
        return

    plan = ensure_plan_scaffold(user)
    pfa_choice = PFA_MENU_ORDER[int(reply) - 1]
    plan.preferred_pfa = pfa_choice
    plan.save(update_fields=["preferred_pfa", "updated_at"])

    send_message(
        user=user,
        session=session,
        body=(
            f"Do you already have an RSA PIN registered with {pfa_choice.label}? "
            "Reply with your RSA PIN, or reply 0 if you need a new one created."
        ),
    )
    set_session_state(session, ConversationState.ONBOARDING_PFA_LINK)


def handle_pfa_link_reply(user, session, message_log, raw_body):
    reply = raw_body.strip()
    plan = ensure_plan_scaffold(user)

    if reply != "0":
        if not _looks_like_rsa_pin(reply):
            send_message(
                user=user,
                session=session,
                body="That doesn't look like a valid RSA PIN. Reply with your RSA PIN, or reply 0 for a new one.",
            )
            return
        # User already has a real RSA PIN - link it directly, no mock
        # registration call needed (pensions.services.register_with_pfa
        # already no-ops once pfa_registration_status is REGISTERED).
        plan.rsa_pin = reply
        plan.pfa_registration_status = PFARegistrationStatus.REGISTERED
        plan.pfa_registered_at = timezone.now()
        plan.save(update_fields=["rsa_pin", "pfa_registration_status", "pfa_registered_at", "updated_at"])
        send_message(user=user, session=session, body=f"Got it - linked to {plan.get_preferred_pfa_display()}.")

    _proceed_to_consent(user, session, plan)


def _proceed_to_consent(user, session, plan):
    pfa_label = plan.get_preferred_pfa_display() if plan.preferred_pfa else "your chosen PFA"
    send_message(user=user, session=session, body=TERMS_SUMMARY.format(pfa=pfa_label))
    set_session_state(session, ConversationState.ONBOARDING_CONSENT)


def handle_consent_reply(user, session, message_log, raw_body):
    reply = raw_body.strip().lower()
    if reply not in {"1", "agree", "i agree", "yes"}:
        plan = ensure_plan_scaffold(user)
        pfa_label = plan.get_preferred_pfa_display() if plan.preferred_pfa else "your chosen PFA"
        send_message(user=user, session=session, body="Reply 1 to agree and continue.\n\n" + TERMS_SUMMARY.format(pfa=pfa_label))
        return

    now = timezone.now()
    sid = message_log.twilio_message_sid or ""
    ConsentRecord.objects.create(
        user=user,
        consent_type=ConsentType.DATA_PROCESSING,
        consent_text_version=CONSENT_TEXT_VERSION,
        accepted_at=now,
        source_message_sid=sid,
    )
    ConsentRecord.objects.create(
        user=user,
        consent_type=ConsentType.TERMS_OF_SERVICE,
        consent_text_version=CONSENT_TEXT_VERSION,
        accepted_at=now,
        source_message_sid=sid,
    )
    user.onboarding_state = OnboardingState.CONSENT_GIVEN
    user.save(update_fields=["onboarding_state", "updated_at"])

    _attempt_pfa_registration(user, session)

    send_message(
        user=user,
        session=session,
        body="Last step: set a 4-digit PIN. You'll use this to confirm every contribution. Reply with 4 digits now.",
    )
    set_session_state(session, ConversationState.ONBOARDING_PIN_SETUP)


def _attempt_pfa_registration(user, session):
    plan = register_with_pfa(user)
    if plan.pfa_registration_status == PFARegistrationStatus.REGISTERED:
        send_message(
            user=user,
            session=session,
            body=f"You're registered with {plan.get_preferred_pfa_display()}. Your RSA PIN: {plan.rsa_pin}",
        )
    elif plan.pfa_registration_status == PFARegistrationStatus.PENDING:
        send_message(
            user=user,
            session=session,
            body=f"Your registration with {plan.get_preferred_pfa_display()} is being processed - we'll confirm your RSA PIN once it's ready.",
        )
    else:
        # FAILED - never block onboarding on this; conversations.tasks/pensions.tasks
        # retries it in the background (see pensions.tasks.retry_pfa_registrations_task).
        send_message(
            user=user,
            session=session,
            body="We couldn't reach your PFA to register right now, but your BabaSika savings will still work - we'll keep trying in the background.",
        )


def handle_pin_setup_reply(user, session, message_log, raw_body):
    raw_pin = raw_body.strip()
    error = validate_transaction_pin(raw_pin)
    if error:
        send_message(user=user, session=session, body=f"{error} Reply with 4 digits.")
        return

    user.set_transaction_pin(raw_pin)
    user.onboarding_state = OnboardingState.COMPLETED
    user.save(
        update_fields=[
            "transaction_pin_hash",
            "pin_attempt_count",
            "pin_locked_until",
            "onboarding_state",
            "updated_at",
        ]
    )
    ConsentRecord.objects.create(
        user=user,
        consent_type=ConsentType.PIN_SETUP,
        consent_text_version=CONSENT_TEXT_VERSION,
        accepted_at=timezone.now(),
        source_message_sid=message_log.twilio_message_sid or "",
    )

    dashboard_url, _ = issue_magic_link(user, requested_via=MagicLinkRequestSource.ONBOARDING_COMPLETE)
    send_message(
        user=user,
        session=session,
        body=(
            "You're all set! \U0001F389 Whenever you get paid, just message BabaSika and I'll "
            "suggest how much to set aside.\n\n"
            f"View your dashboard here (link expires in 15 min): {dashboard_url}"
        ),
    )
    set_session_state(session, ConversationState.IDLE, context={})
