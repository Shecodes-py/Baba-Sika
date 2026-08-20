import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from ai_engine.models import AIInteractionLog
from babasika.base_models import TimeStampedModel, UUIDPrimaryKeyModel

# v1 decision: fixed ratio per plan, not AI-dynamic per contribution.
# Clamped so onboarding/admin error can't produce a 0% or 100% split.
MIN_EMERGENCY_RATIO = Decimal("0.10")
MAX_EMERGENCY_RATIO = Decimal("0.50")
DEFAULT_EMERGENCY_RATIO = Decimal("0.30")

DEFAULT_PENDING_ACTION_TTL_MINUTES = 15


class PensionPlanStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    CLOSED = "closed", "Closed"


class PFAChoice(models.TextChoices):
    """
    Candidate list for the onboarding picker only - none of these are
    integrated. "Which PFA" is captured as a user preference; the actual
    registration (pensions.providers.PFAProvider) is entirely mocked until a
    direct commercial partnership with one of these exists.
    """

    STANBIC_IBTC = "stanbic_ibtc", "Stanbic IBTC Pension Managers"
    ARM = "arm", "ARM Pension Managers"
    LEADWAY_PENSURE = "leadway_pensure", "Leadway Pensure PFA"
    FCMB = "fcmb", "FCMB Pensions"
    PAL = "pal", "Pensions Alliance Limited (PAL)"
    TRUSTFUND = "trustfund", "Trustfund Pensions"
    CRUSADER_STERLING = "crusader_sterling", "Crusader Sterling Pensions"
    PREMIUM = "premium", "Premium Pension"
    SIGMA = "sigma", "Sigma Pensions"
    FIDELITY = "fidelity", "Fidelity Pension Managers"
    PARTHIAN = "parthian", "Parthian Pensions"
    CITIZENS = "citizens", "Citizens Pensions"


class PFARegistrationStatus(models.TextChoices):
    NOT_REGISTERED = "not_registered", "Not registered"
    PENDING = "pending", "Pending"
    REGISTERED = "registered", "Registered"
    FAILED = "failed", "Failed"


class PensionPlan(UUIDPrimaryKeyModel, TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pension_plan"
    )
    status = models.CharField(
        max_length=10, choices=PensionPlanStatus.choices, default=PensionPlanStatus.ACTIVE
    )
    retirement_target_age = models.PositiveSmallIntegerField(default=60)
    emergency_ratio = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=DEFAULT_EMERGENCY_RATIO,
        validators=[MinValueValidator(MIN_EMERGENCY_RATIO), MaxValueValidator(MAX_EMERGENCY_RATIO)],
        help_text="Fraction of each confirmed contribution routed to the emergency fund; the rest goes to retirement. Deterministic split - never set by AI.",
    )

    # PFA enrollment - see pensions.providers.PFAProvider. Entirely mocked;
    # rsa_pin/registration_status only ever come from that interface, never
    # set directly.
    preferred_pfa = models.CharField(max_length=25, choices=PFAChoice.choices, blank=True)
    rsa_pin = models.CharField(max_length=20, blank=True)
    pfa_registration_status = models.CharField(
        max_length=15, choices=PFARegistrationStatus.choices, default=PFARegistrationStatus.NOT_REGISTERED
    )
    pfa_registered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Plan({self.user})"

    @property
    def retirement_ratio(self) -> Decimal:
        return Decimal("1") - self.emergency_ratio


class ContributionFrequency(models.TextChoices):
    PER_INCOME_EVENT = "per_income_event", "Per income event"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    MANUAL = "manual", "Manual"


class ContributionSchedule(UUIDPrimaryKeyModel, TimeStampedModel):
    """Nudge cadence policy - drives the Celery beat reminder task, not the actual split math."""

    plan = models.ForeignKey(PensionPlan, on_delete=models.CASCADE, related_name="schedules")
    frequency = models.CharField(max_length=20, choices=ContributionFrequency.choices)
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.plan.user} - {self.frequency}"


class PendingActionType(models.TextChoices):
    CONTRIBUTION = "contribution", "Contribution"
    ADJUST_SCHEDULE = "adjust_schedule", "Adjust schedule"


class PendingActionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    EXECUTING = "executing", "Executing"
    EXECUTED = "executed", "Executed"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"
    FAILED = "failed", "Failed"


def default_expiry():
    return timezone.now() + timezone.timedelta(minutes=DEFAULT_PENDING_ACTION_TTL_MINUTES)


class PendingAction(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    The safety gate. AI only ever writes a PendingAction (via
    pensions.services.create_pending_action_from_ai) - nothing touches Wema
    until a user reply flips this to CONFIRMED and the PIN checks out, at
    which point pensions.services.execute_pending_action runs the transfer
    exactly once (idempotency_key dedupes retries).
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pending_actions")
    action_type = models.CharField(max_length=20, choices=PendingActionType.choices)
    proposed_payload = models.JSONField(default=dict, blank=True)
    ai_interaction_log = models.ForeignKey(
        AIInteractionLog, on_delete=models.SET_NULL, null=True, blank=True, related_name="pending_actions"
    )
    idempotency_key = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=15, choices=PendingActionStatus.choices, default=PendingActionStatus.PENDING
    )
    expires_at = models.DateTimeField(default=default_expiry)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    pin_verified = models.BooleanField(default=False)
    confirmation_message_sid = models.CharField(max_length=64, blank=True)
    decline_reason = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self):
        return f"{self.action_type} - {self.user} - {self.status}"

    @property
    def is_expired(self) -> bool:
        return self.status == PendingActionStatus.PENDING and timezone.now() >= self.expires_at


class ContributionDestination(models.TextChoices):
    EMERGENCY_FUND = "emergency_fund", "Emergency fund"
    RETIREMENT_FUND = "retirement_fund", "Retirement fund"


class ContributionStatus(models.TextChoices):
    EXECUTED = "executed", "Executed"
    FAILED = "failed", "Failed"
    REVERSED = "reversed", "Reversed"


class Contribution(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    The actual ledger-facing record, one per bucket (an approved total is
    split into up to two of these - emergency + retirement). Only ever
    created by pensions.services.execute_pending_action, after a real
    (or mock) Wema transfer succeeds.
    """

    plan = models.ForeignKey(PensionPlan, on_delete=models.CASCADE, related_name="contributions")
    pending_action = models.ForeignKey(
        PendingAction, on_delete=models.PROTECT, related_name="contributions"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    destination = models.CharField(max_length=20, choices=ContributionDestination.choices)
    bank_transfer_reference = models.CharField(max_length=128, blank=True)
    # Only ever set on the retirement_fund row, and only best-effort - a
    # failed/skipped PFA remittance never blocks or reverses the underlying
    # bank transfer, which is the real ledger of record. See
    # pensions.services.execute_pending_action.
    pfa_remittance_reference = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=10, choices=ContributionStatus.choices)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.destination} {self.amount} - {self.plan.user}"


class EmergencyFund(UUIDPrimaryKeyModel, TimeStampedModel):
    """Shadow-ledger balance - computed from Contribution rows, not a separate Wema balance."""

    plan = models.OneToOneField(PensionPlan, on_delete=models.CASCADE, related_name="emergency_fund")
    target_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    current_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"EmergencyFund({self.plan.user}) = {self.current_balance}"


class RetirementTracker(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    Shadow-ledger balance - same caveat as EmergencyFund. `readiness_score`
    is a cached copy of the last computed value from
    pensions.services.compute_retirement_readiness (a placeholder heuristic -
    see that function's docstring); always recomputed fresh for the
    balance/progress-check flow, this field just makes the last value
    visible in admin without recomputation.
    """

    plan = models.OneToOneField(PensionPlan, on_delete=models.CASCADE, related_name="retirement_tracker")
    current_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    readiness_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    readiness_label = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"RetirementTracker({self.plan.user}) = {self.current_balance}"


# --- MockPFAProvider's own storage -------------------------------------------
# Same rationale as account_provisioning.models.MockLedgerAccount/Transaction:
# this simulates the PFA/PenCom's own records, separate from PensionPlan's
# rsa_pin/pfa_registration_status (BabaSika's cached view of them). Only
# pensions.providers.mock reads/writes these.

class MockPFARegistration(UUIDPrimaryKeyModel, TimeStampedModel):
    idempotency_key = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mock_pfa_registrations")
    rsa_pin = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=15, choices=PFARegistrationStatus.choices)
    raw_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user} - {self.status} ({self.rsa_pin or 'no PIN yet'})"


class MockPFASubmission(UUIDPrimaryKeyModel, TimeStampedModel):
    rsa_pin = models.CharField(max_length=20, db_index=True)
    idempotency_key = models.CharField(max_length=64, unique=True)
    remittance_ref = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=15, default="successful")
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.rsa_pin} - {self.amount}"
