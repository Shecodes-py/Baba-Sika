"""
MockWemaProvider - the only BankProvider implementation shipped today.
Simulates account creation and transfers against our own DB (MockLedgerAccount/
MockLedgerTransaction - see account_provisioning.models), with realistic
latency and two distinct failure modes:
  - a random simulated outage (settings.MOCK_PROVIDER_FAILURE_RATE)
  - a deterministic "insufficient funds" failure when a transfer exceeds the
    account's simulated balance

Both are things conversations.flows already has to handle (see
onboarding._attempt_bank_link's retry path and pensions.services.execute_pending_action's
FAILED-status path).
"""

import random
import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from babasika.mock_provider_utils import maybe_raise, simulate_latency

from ..models import MockLedgerAccount, MockLedgerTransaction, TransactionDirection
from .base import AccountResult, BalanceResult, BankProvider, BankProviderError, TransactionRecord, TransferResult

# New mock accounts start with a random balance in this range so contribution
# amounts sometimes genuinely exceed it (a realistic failure, not just noise).
SEED_BALANCE_MIN = Decimal("20000.00")
SEED_BALANCE_MAX = Decimal("300000.00")


class MockWemaProvider(BankProvider):
    def create_account(self, user) -> AccountResult:
        simulate_latency()
        maybe_raise(BankProviderError, "Simulated provider outage during account creation")

        account_ref = f"MOCK-{uuid.uuid4().hex[:12].upper()}"
        seed_balance = Decimal(random.uniform(float(SEED_BALANCE_MIN), float(SEED_BALANCE_MAX))).quantize(
            Decimal("0.01")
        )
        MockLedgerAccount.objects.create(account_ref=account_ref, balance=seed_balance)
        return AccountResult(
            account_ref=account_ref,
            masked_account_number="******" + str(uuid.uuid4().int)[:4],
            raw_response={"mock": True, "user": str(user.pk), "seed_balance": str(seed_balance)},
        )

    def get_balance(self, account_ref: str) -> BalanceResult:
        simulate_latency()
        ledger_account = MockLedgerAccount.objects.get(account_ref=account_ref)
        return BalanceResult(
            available_balance=ledger_account.balance,
            as_of=timezone.now().isoformat(),
            raw_response={"mock": True, "account_ref": account_ref},
        )

    def initiate_transfer(
        self, account_ref: str, amount: Decimal, purpose: str, *, idempotency_key: str
    ) -> TransferResult:
        simulate_latency()

        existing = MockLedgerTransaction.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            # Same idempotency key as a prior call - return the original result
            # instead of transferring again, even at this "external system" layer.
            return TransferResult(
                transfer_ref=existing.transfer_ref,
                status="successful",
                raw_response={"mock": True, "deduped": True},
            )

        maybe_raise(BankProviderError, "Simulated provider outage during transfer")

        with transaction.atomic():
            ledger_account = MockLedgerAccount.objects.select_for_update().get(account_ref=account_ref)
            if amount > ledger_account.balance:
                raise BankProviderError(
                    f"Insufficient funds: balance {ledger_account.balance} < requested {amount}"
                )
            ledger_account.balance -= amount
            ledger_account.save(update_fields=["balance", "updated_at"])

            transfer_ref = f"MOCKXFER-{uuid.uuid4().hex[:16].upper()}"
            MockLedgerTransaction.objects.create(
                account_ref=account_ref,
                idempotency_key=idempotency_key,
                transfer_ref=transfer_ref,
                amount=amount,
                direction=TransactionDirection.DEBIT,
                purpose=purpose,
                occurred_at=timezone.now(),
            )

        return TransferResult(
            transfer_ref=transfer_ref,
            status="successful",
            raw_response={"mock": True, "account_ref": account_ref, "amount": str(amount), "purpose": purpose},
        )

    def get_transaction_history(self, account_ref: str, *, since: str | None = None) -> list[TransactionRecord]:
        simulate_latency()
        qs = MockLedgerTransaction.objects.filter(account_ref=account_ref)
        if since:
            qs = qs.filter(occurred_at__gte=since)
        return [
            TransactionRecord(
                transaction_ref=t.transfer_ref,
                amount=t.amount,
                direction=t.direction,
                narration=t.purpose,
                occurred_at=t.occurred_at.isoformat(),
                raw_response={"mock": True},
            )
            for t in qs
        ]
