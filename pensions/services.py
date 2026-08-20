"""
The deterministic ledger engine. This module is the ONLY place money moves
or a PFA is contacted in the whole codebase - it never calls ai_engine, and
the only thing it takes from AI output is a plain "suggested_amount" number
that a human has since confirmed via a numbered WhatsApp reply + PIN.
Splitting a confirmed amount into emergency/retirement buckets is pure
arithmetic against PensionPlan.emergency_ratio - the AI never sees or
influences the split, and neither BankProvider nor PFAProvider ever sees
raw AI output, only amounts a human already confirmed.
"""

import logging
import time
import uuid
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from account_provisioning.models import BankAccountLink, ProviderCallStatus, ProviderType
from account_provisioning.providers import BankProviderError
from account_provisioning.services import log_provider_call, transfer_funds

from .models import (
    Contribution,
    ContributionDestination,
    ContributionStatus,
    EmergencyFund,
    PendingAction,
    PendingActionStatus,
    PensionPlan,
    PFARegistrationStatus,
    RetirementTracker,
)
from .providers import PFAProviderError, get_pfa_provider

logger = logging.getLogger(__name__)


class PensionServiceError(Exception):
    pass


class PinLockedError(PensionServiceError):
    pass


class PinIncorrectError(PensionServiceError):
    pass


class PendingActionNotActionableError(PensionServiceError):
    """Raised when confirming/declining an action that isn't in PENDING state, or has expired."""


# --- plan scaffolding --------------------------------------------------------

def ensure_plan_scaffold(user) -> PensionPlan:
    """Idempotent: creates the PensionPlan + its two fund trackers if missing."""
    plan, _ = PensionPlan.objects.get_or_create(user=user)
    EmergencyFund.objects.get_or_create(plan=plan)
    RetirementTracker.objects.get_or_create(plan=plan)
    return plan


# --- PFA registration ---------------------------------------------------------
# Best-effort by design: a failed/pending PFA registration never blocks
# onboarding or a contribution's bank transfer - the PFA partnership is a
# separate BD conversation, not a dependency of the core WhatsApp savings
# habit. See pensions.providers.PFAProvider's docstring.

def register_with_pfa(user) -> PensionPlan:
    plan = ensure_plan_scaffold(user)
    if plan.pfa_registration_status == PFARegistrationStatus.REGISTERED:
        return plan

    kyc_data = {
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "occupation_type": user.occupation_type,
        "preferred_pfa": plan.preferred_pfa,
    }
    # A fresh key per attempt (not a stable one) is deliberate: unlike a bank
    # transfer, this call may legitimately need re-attempting later (see
    # pensions.tasks.retry_pfa_registrations_task) if PenCom hasn't issued a
    # PIN yet - a stable key would keep returning the same cached "pending"
    # forever via MockPFAProvider's own dedupe.
    idempotency_key = f"pfa-register-{plan.pk}-{uuid.uuid4().hex[:8]}"

    provider = get_pfa_provider()
    start = time.monotonic()
    try:
        result = provider.register_contributor(user, kyc_data, idempotency_key=idempotency_key)
    except PFAProviderError as exc:
        log_provider_call(
            provider_type=ProviderType.PFA,
            method_name="register_contributor",
            user=user,
            idempotency_key=idempotency_key,
            request_payload=kyc_data,
            response_payload={},
            status=ProviderCallStatus.FAILED,
            error_message=str(exc),
            latency_ms=int((time.monotonic() - start) * 1000),
        )
        plan.pfa_registration_status = PFARegistrationStatus.FAILED
        plan.save(update_fields=["pfa_registration_status", "updated_at"])
        return plan

    log_provider_call(
        provider_type=ProviderType.PFA,
        method_name="register_contributor",
        user=user,
        idempotency_key=idempotency_key,
        request_payload=kyc_data,
        response_payload=result.raw_response,
        status=ProviderCallStatus.SUCCESS,
        latency_ms=int((time.monotonic() - start) * 1000),
    )

    plan.rsa_pin = result.rsa_pin
    plan.pfa_registration_status = result.status
    if result.status == PFARegistrationStatus.REGISTERED:
        plan.pfa_registered_at = timezone.now()
    plan.save(update_fields=["rsa_pin", "pfa_registration_status", "pfa_registered_at", "updated_at"])
    return plan


def _submit_retirement_contribution_to_pfa(*, user, plan: PensionPlan, pending_action: PendingAction, amount: Decimal) -> str:
    """
    Best-effort remittance of the retirement-fund portion to the user's RSA.
    Returns the remittance_ref, or "" if skipped/failed - the bank transfer
    already succeeded and is the real ledger of record; a PFA hiccup is
    logged, not fatal.
    """
    if plan.pfa_registration_status != PFARegistrationStatus.REGISTERED or not plan.rsa_pin:
        return ""

    provider = get_pfa_provider()
    idempotency_key = str(pending_action.idempotency_key)
    start = time.monotonic()
    try:
        result = provider.submit_contribution(plan.rsa_pin, amount, idempotency_key=idempotency_key)
    except PFAProviderError as exc:
        log_provider_call(
            provider_type=ProviderType.PFA,
            method_name="submit_contribution",
            user=user,
            idempotency_key=idempotency_key,
            request_payload={"rsa_pin": plan.rsa_pin, "amount": str(amount)},
            response_payload={},
            status=ProviderCallStatus.FAILED,
            error_message=str(exc),
            latency_ms=int((time.monotonic() - start) * 1000),
        )
        logger.warning("PFA remittance failed for pending_action=%s: %s", pending_action.pk, exc)
        return ""

    log_provider_call(
        provider_type=ProviderType.PFA,
        method_name="submit_contribution",
        user=user,
        idempotency_key=idempotency_key,
        request_payload={"rsa_pin": plan.rsa_pin, "amount": str(amount)},
        response_payload=result.raw_response,
        status=ProviderCallStatus.SUCCESS,
        latency_ms=int((time.monotonic() - start) * 1000),
    )
    return result.remittance_ref


# --- PendingAction lifecycle --------------------------------------------------

def create_pending_action_from_recommendation(*, user, parsed_output: dict, ai_log, source_context: dict):
    """
    Called right after ai_engine.services.generate_recommendation returns.
    Writes the PendingAction; still nothing touches the bank or a PFA.
    """
    payload = {
        "suggested_amount": parsed_output.get("suggested_amount"),
        "whatsapp_copy": parsed_output.get("whatsapp_copy", ""),
        "reasoning": parsed_output.get("reasoning", ""),
        "source_context": source_context,
    }
    return PendingAction.objects.create(
        user=user,
        action_type="contribution",
        proposed_payload=payload,
        ai_interaction_log=ai_log,
    )


def expire_stale_pending_actions() -> int:
    """Run periodically by Celery beat. Returns the number of rows expired."""
    stale = PendingAction.objects.filter(
        status=PendingActionStatus.PENDING, expires_at__lte=timezone.now()
    )
    return stale.update(status=PendingActionStatus.EXPIRED, decline_reason="expired")


def decline_pending_action(pending_action: PendingAction, *, reason: str = "user_skipped") -> PendingAction:
    if pending_action.status != PendingActionStatus.PENDING:
        raise PendingActionNotActionableError(f"PendingAction is {pending_action.status}, not pending")
    pending_action.status = PendingActionStatus.CANCELLED
    pending_action.decline_reason = reason
    pending_action.save(update_fields=["status", "decline_reason", "updated_at"])
    return pending_action


def confirm_and_execute_pending_action(
    pending_action: PendingAction, *, raw_pin: str, message_sid: str = ""
) -> PendingAction:
    """
    The single entry point conversations.flows uses after a user replies
    "1" (approve) and then supplies their PIN. Raises PinLockedError /
    PinIncorrectError / PendingActionNotActionableError - callers translate
    those into the right WhatsApp copy without ever retrying the transfer
    themselves (idempotency is handled inside execute_pending_action).
    """
    if pending_action.status != PendingActionStatus.PENDING:
        raise PendingActionNotActionableError(f"PendingAction is {pending_action.status}, not pending")
    if pending_action.is_expired:
        pending_action.status = PendingActionStatus.EXPIRED
        pending_action.decline_reason = "expired"
        pending_action.save(update_fields=["status", "decline_reason", "updated_at"])
        raise PendingActionNotActionableError("PendingAction expired")

    user = pending_action.user
    if user.is_pin_locked():
        raise PinLockedError("Transaction PIN is locked due to too many failed attempts")
    if not user.check_transaction_pin(raw_pin):
        raise PinIncorrectError("Incorrect transaction PIN")

    pending_action.status = PendingActionStatus.CONFIRMED
    pending_action.confirmed_at = timezone.now()
    pending_action.pin_verified = True
    pending_action.confirmation_message_sid = message_sid
    pending_action.save(
        update_fields=["status", "confirmed_at", "pin_verified", "confirmation_message_sid", "updated_at"]
    )

    return execute_pending_action(pending_action)


def execute_pending_action(pending_action: PendingAction) -> PendingAction:
    """
    Fires exactly once per PendingAction: one BankProvider transfer, keyed
    on pending_action.idempotency_key, then splits the confirmed total into
    two Contribution rows via PensionPlan.emergency_ratio - pure arithmetic,
    no further bank calls, no AI involvement. If the user is registered with
    a PFA, the retirement-fund portion is then best-effort remitted via
    PFAProvider - a PFA hiccup is logged but never blocks or reverses the
    already-successful bank transfer.
    """
    if pending_action.status not in (PendingActionStatus.CONFIRMED, PendingActionStatus.EXECUTING):
        raise PendingActionNotActionableError(
            f"PendingAction must be CONFIRMED to execute, was {pending_action.status}"
        )

    # Idempotency guard: if a retry lands here after a prior call already
    # produced Contribution rows for this PendingAction, don't transfer again.
    if Contribution.objects.filter(pending_action=pending_action).exists():
        pending_action.status = PendingActionStatus.EXECUTED
        pending_action.save(update_fields=["status", "updated_at"])
        return pending_action

    try:
        amount = Decimal(str(pending_action.proposed_payload.get("suggested_amount")))
    except (InvalidOperation, TypeError):
        pending_action.status = PendingActionStatus.FAILED
        pending_action.decline_reason = "invalid_amount"
        pending_action.save(update_fields=["status", "decline_reason", "updated_at"])
        raise PensionServiceError("PendingAction has no valid suggested_amount")

    pending_action.status = PendingActionStatus.EXECUTING
    pending_action.save(update_fields=["status", "updated_at"])

    user = pending_action.user
    plan = ensure_plan_scaffold(user)
    if not BankAccountLink.objects.filter(user=user).exists():
        pending_action.status = PendingActionStatus.FAILED
        pending_action.decline_reason = "no_linked_account"
        pending_action.save(update_fields=["status", "decline_reason", "updated_at"])
        raise PensionServiceError("User has no provisioned account")

    try:
        transfer = transfer_funds(
            user=user,
            amount=amount,
            purpose="BabaSika pension contribution",
            idempotency_key=str(pending_action.idempotency_key),
        )
    except BankProviderError as exc:
        pending_action.status = PendingActionStatus.FAILED
        pending_action.decline_reason = "transfer_failed"
        pending_action.save(update_fields=["status", "decline_reason", "updated_at"])
        logger.error("Transfer failed for pending_action=%s: %s", pending_action.pk, exc)
        raise

    emergency_amount = (amount * plan.emergency_ratio).quantize(Decimal("0.01"))
    retirement_amount = amount - emergency_amount

    pfa_remittance_reference = _submit_retirement_contribution_to_pfa(
        user=user, plan=plan, pending_action=pending_action, amount=retirement_amount
    )

    with transaction.atomic():
        Contribution.objects.create(
            plan=plan,
            pending_action=pending_action,
            amount=emergency_amount,
            destination=ContributionDestination.EMERGENCY_FUND,
            bank_transfer_reference=transfer.transfer_ref,
            status=ContributionStatus.EXECUTED,
            executed_at=timezone.now(),
        )
        Contribution.objects.create(
            plan=plan,
            pending_action=pending_action,
            amount=retirement_amount,
            destination=ContributionDestination.RETIREMENT_FUND,
            bank_transfer_reference=transfer.transfer_ref,
            pfa_remittance_reference=pfa_remittance_reference,
            status=ContributionStatus.EXECUTED,
            executed_at=timezone.now(),
        )

        emergency_fund = EmergencyFund.objects.select_for_update().get(plan=plan)
        emergency_fund.current_balance += emergency_amount
        emergency_fund.save(update_fields=["current_balance", "updated_at"])

        retirement_tracker = RetirementTracker.objects.select_for_update().get(plan=plan)
        retirement_tracker.current_balance += retirement_amount
        retirement_tracker.save(update_fields=["current_balance", "updated_at"])

        pending_action.status = PendingActionStatus.EXECUTED
        pending_action.save(update_fields=["status", "updated_at"])

    compute_retirement_readiness(plan, persist=True)
    return pending_action


# --- read-only progress / readiness ------------------------------------------

def compute_retirement_readiness(plan: PensionPlan, *, persist: bool = False) -> dict:
    """
    PLACEHOLDER HEURISTIC - v1 has no date-of-birth, target retirement
    income, or actuarial input collected anywhere in onboarding, so this is
    deliberately simple and should be replaced once product/actuarial input
    is available:

      - If we have logged income history, target = 3x the user's trailing
        average monthly credit (a rough "3-month buffer" milestone covering
        both buckets combined).
      - Otherwise, fall back to a coarse tier based on how many contributions
        have executed so far.

    Returns {"score": 0-100, "label": str, "basis": str} and, if persist,
    writes it onto the RetirementTracker cache fields.
    """
    from account_provisioning.models import BankTransactionMirror, TransactionDirection

    emergency_fund = EmergencyFund.objects.get(plan=plan)
    retirement_tracker = RetirementTracker.objects.get(plan=plan)
    total_saved = emergency_fund.current_balance + retirement_tracker.current_balance

    recent_credits = BankTransactionMirror.objects.filter(
        user=plan.user, direction=TransactionDirection.CREDIT
    ).order_by("-occurred_at")[:6]

    if recent_credits:
        avg_income = sum((t.amount for t in recent_credits), Decimal("0")) / len(recent_credits)
        target = (avg_income * 3).quantize(Decimal("0.01")) if avg_income > 0 else None
    else:
        target = None

    if target and target > 0:
        score = min(Decimal("100"), (total_saved / target) * 100).quantize(Decimal("0.01"))
        basis = "3x trailing average monthly income"
    else:
        contribution_count = Contribution.objects.filter(plan=plan, status=ContributionStatus.EXECUTED).count()
        score = Decimal(min(100, contribution_count * 10))
        basis = "contribution count (no income history yet)"

    if score < 25:
        label = "Just getting started"
    elif score < 50:
        label = "Building momentum"
    elif score < 75:
        label = "Steady saver"
    else:
        label = "On track"

    result = {"score": float(score), "label": label, "basis": basis}

    if persist:
        retirement_tracker.readiness_score = score
        retirement_tracker.readiness_label = label
        retirement_tracker.save(update_fields=["readiness_score", "readiness_label", "updated_at"])

    return result


def get_progress_summary(user) -> dict:
    """Read-only. No AI. Used by the balance/progress-check WhatsApp flow and the dashboard API."""
    plan = ensure_plan_scaffold(user)
    emergency_fund = EmergencyFund.objects.get(plan=plan)
    retirement_tracker = RetirementTracker.objects.get(plan=plan)
    readiness = compute_retirement_readiness(plan, persist=True)

    bank_balance = None
    try:
        bank_balance = BankAccountLink.objects.get(user=user).last_known_balance
    except BankAccountLink.DoesNotExist:
        pass

    return {
        "emergency_fund_balance": emergency_fund.current_balance,
        "emergency_fund_target": emergency_fund.target_amount,
        "retirement_balance": retirement_tracker.current_balance,
        "retirement_readiness": readiness,
        "bank_account_balance": bank_balance,
        "emergency_ratio": plan.emergency_ratio,
        "preferred_pfa": plan.preferred_pfa,
        "pfa_registration_status": plan.pfa_registration_status,
        "rsa_pin": plan.rsa_pin,
    }
