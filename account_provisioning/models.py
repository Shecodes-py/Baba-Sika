from django.conf import settings
from django.db import models

from babasika.base_models import TimeStampedModel, UUIDPrimaryKeyModel


class BankLinkStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    LINKED = "linked", "Linked"
    FAILED = "failed", "Failed"
    DELINKED = "delinked", "Delinked"


class BankAccountLink(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    BabaSika's cached view of the user's provisioned account - one per user.
    `last_known_balance` is synced FROM the provider (account_provisioning.services.sync_balance),
    never written to directly; it is not the source of truth (the provider is).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_account_link"
    )
    account_ref = models.CharField(max_length=128, blank=True)
    masked_account_number = models.CharField(max_length=32, blank=True)
    status = models.CharField(
        max_length=15, choices=BankLinkStatus.choices, default=BankLinkStatus.PENDING
    )
    last_known_balance = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    last_balance_synced_at = models.DateTimeField(null=True, blank=True)
    link_raw_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user} -> {self.account_ref or '(unlinked)'}"


class TransactionDirection(models.TextChoices):
    CREDIT = "credit", "Credit"
    DEBIT = "debit", "Debit"


class BankTransactionMirror(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    Local mirror of the provider's transaction history, used for AI pattern
    analysis and read-only queries without hitting the provider on every
    request. Also written to directly for manually-logged income (see
    conversations.flows.income), which never touches the provider at all.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_transactions"
    )
    transaction_ref = models.CharField(max_length=128, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    direction = models.CharField(max_length=10, choices=TransactionDirection.choices)
    narration = models.CharField(max_length=255, blank=True)
    occurred_at = models.DateTimeField()
    raw_payload = models.JSONField(default=dict, blank=True)
    synced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["user", "-occurred_at"])]

    def __str__(self):
        return f"{self.direction} {self.amount} - {self.user}"


# --- MockWemaProvider's own storage ------------------------------------------
# Deliberately separate from BankAccountLink/BankTransactionMirror above:
# those represent what BabaSika believes (synced FROM a provider); these
# represent the simulated external bank's own ledger. A real provider
# implementation would have no equivalent - its ledger lives at the bank.
# Only account_provisioning.providers.mock reads/writes these.

class MockLedgerAccount(UUIDPrimaryKeyModel, TimeStampedModel):
    account_ref = models.CharField(max_length=64, unique=True)
    balance = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"{self.account_ref} = {self.balance}"


class MockLedgerTransaction(UUIDPrimaryKeyModel, TimeStampedModel):
    account_ref = models.CharField(max_length=64, db_index=True)
    idempotency_key = models.CharField(max_length=64, unique=True)
    transfer_ref = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    direction = models.CharField(max_length=10, choices=TransactionDirection.choices)
    purpose = models.CharField(max_length=255, blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["-occurred_at"]


# --- Provider call audit trail ------------------------------------------------
# Lives here (not in pensions) so both this app's BankProvider calls and
# pensions' PFAProvider calls can log to the same table without a circular
# import - pensions already depends on account_provisioning, never the
# reverse. Mirrors ai_engine.AIInteractionLog's shape/intent: this is
# financial/compliance-adjacent data, so every call is logged, success or
# failure, and rows are never mutated after creation.

class ProviderType(models.TextChoices):
    BANK = "bank", "Bank"
    PFA = "pfa", "PFA"


class ProviderCallStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


class ProviderCallLog(UUIDPrimaryKeyModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="provider_calls",
    )
    provider_type = models.CharField(max_length=10, choices=ProviderType.choices)
    method_name = models.CharField(max_length=50)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=10, choices=ProviderCallStatus.choices)
    error_message = models.TextField(blank=True)
    latency_ms = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider_type}.{self.method_name} - {self.status} @ {self.created_at}"
