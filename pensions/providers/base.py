"""
PFAProvider interface.

There is no public PFA API. PenCom's ECRS is PFA-to-PenCom only - registering
a Micro/Personal Pension Plan contributor requires a licensed PFA itself to
capture biometrics/KYC and submit to PenCom for an RSA PIN. That has to go
through a direct commercial partnership with a specific PFA, which hasn't
landed yet. This interface exists so that partnership, whenever it happens,
is a second class implementing the same three methods - nothing else in the
codebase should need to change. Today the only implementation is
MockPFAProvider (mock.py).

Response shapes are loosely modeled on what PenCom's guidelines describe
(RSA PIN issued after PFA-mediated registration; registration can be
pending before PenCom issues the PIN) - this is for a plausible mock shape,
not a confirmed real one.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class RegistrationResult:
    rsa_pin: str  # blank if status is not "registered" yet
    status: str  # "pending" | "registered" | "failed"
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContributionStatusResult:
    rsa_pin: str
    total_contributed: Decimal
    contribution_count: int
    last_contribution_at: str | None
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubmissionResult:
    remittance_ref: str
    status: str  # "successful" | "pending" | "failed"
    raw_response: dict[str, Any] = field(default_factory=dict)


class PFAProviderError(Exception):
    """Raised for any provider-side failure (simulated outage, rejected submission)."""


class PFAProvider(ABC):
    """
    `idempotency_key` is a required keyword-only argument on
    register_contributor and submit_contribution - the two calls a retry
    could otherwise duplicate against PenCom/the PFA. get_contribution_status
    is read-only.
    """

    @abstractmethod
    def register_contributor(self, user, kyc_data: dict, *, idempotency_key: str) -> RegistrationResult:
        ...

    @abstractmethod
    def get_contribution_status(self, rsa_pin: str) -> ContributionStatusResult:
        ...

    @abstractmethod
    def submit_contribution(self, rsa_pin: str, amount: Decimal, *, idempotency_key: str) -> SubmissionResult:
        ...
