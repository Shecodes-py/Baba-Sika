"""
BankProvider interface.

There is no confirmed Wema API integration yet - BabaSika is currently a
customer-acquisition channel for Wema, not a system wired into their live
rails. This interface exists so the rest of the app (pensions, conversations)
never touches a bank SDK/HTTP client directly. Today the only implementation
is MockWemaProvider (mock.py), which simulates account creation and
transfers entirely against our own DB. When a real Wema (or other bank)
integration is confirmed, it becomes a second class implementing this same
interface - nothing else in the codebase should need to change.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class AccountResult:
    account_ref: str
    masked_account_number: str
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class BalanceResult:
    available_balance: Decimal
    as_of: str
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionRecord:
    transaction_ref: str
    amount: Decimal
    direction: str  # "credit" | "debit"
    narration: str
    occurred_at: str
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class TransferResult:
    transfer_ref: str
    status: str  # "successful" | "pending" | "failed"
    raw_response: dict[str, Any] = field(default_factory=dict)


class BankProviderError(Exception):
    """Raised for any provider-side failure (simulated outage, insufficient funds, rejected transfer)."""


class BankProvider(ABC):
    """
    Positional signatures intentionally match what's specified for the
    swap-in real implementation: create_account(user), get_balance(account_ref),
    initiate_transfer(account_ref, amount, purpose), get_transaction_history(account_ref).
    `idempotency_key` is added as a required keyword-only argument on
    initiate_transfer only, since that's the one call a retry could turn
    into a double-spend - callers always pass PendingAction.idempotency_key.
    """

    @abstractmethod
    def create_account(self, user) -> AccountResult:
        ...

    @abstractmethod
    def get_balance(self, account_ref: str) -> BalanceResult:
        ...

    @abstractmethod
    def initiate_transfer(
        self, account_ref: str, amount: Decimal, purpose: str, *, idempotency_key: str
    ) -> TransferResult:
        ...

    @abstractmethod
    def get_transaction_history(self, account_ref: str, *, since: str | None = None) -> list[TransactionRecord]:
        ...
