"""
MockPFAProvider - the only PFAProvider implementation shipped today.
Simulates PenCom-style RSA PIN issuance (with a realistic pending/registered
split, since PenCom processing isn't instant even for a real PFA) and
contribution remittance, against our own DB (MockPFARegistration/
MockPFASubmission - see pensions.models).
"""

import random
import uuid
from decimal import Decimal

from django.utils import timezone

from babasika.mock_provider_utils import maybe_raise, simulate_latency

from ..models import MockPFARegistration, MockPFASubmission, PFARegistrationStatus
from .base import ContributionStatusResult, PFAProvider, PFAProviderError, RegistrationResult, SubmissionResult

# Most mock registrations resolve immediately for a smooth demo; a minority
# come back "pending" (simulating PenCom not having issued the PIN yet),
# which the WhatsApp flow has to handle without blocking onboarding.
PENDING_RATE = 0.15


class MockPFAProvider(PFAProvider):
    def register_contributor(self, user, kyc_data: dict, *, idempotency_key: str) -> RegistrationResult:
        simulate_latency()

        existing = MockPFARegistration.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return RegistrationResult(
                rsa_pin=existing.rsa_pin, status=existing.status, raw_response=existing.raw_response
            )

        maybe_raise(PFAProviderError, "Simulated PFA/PenCom outage during registration")

        if random.random() < PENDING_RATE:
            status = PFARegistrationStatus.PENDING
            rsa_pin = ""
        else:
            status = PFARegistrationStatus.REGISTERED
            rsa_pin = f"PEN{uuid.uuid4().int % 10**10:010d}"

        raw_response = {
            "mock": True,
            "pfa": kyc_data.get("preferred_pfa", ""),
            "kyc_snapshot": kyc_data,
        }
        MockPFARegistration.objects.create(
            idempotency_key=idempotency_key,
            user=user,
            rsa_pin=rsa_pin,
            status=status,
            raw_response=raw_response,
        )
        return RegistrationResult(rsa_pin=rsa_pin, status=status, raw_response=raw_response)

    def get_contribution_status(self, rsa_pin: str) -> ContributionStatusResult:
        simulate_latency()
        submissions = MockPFASubmission.objects.filter(rsa_pin=rsa_pin, status="successful")
        total = sum((s.amount for s in submissions), Decimal("0.00"))
        last = submissions.order_by("-occurred_at").first()
        return ContributionStatusResult(
            rsa_pin=rsa_pin,
            total_contributed=total,
            contribution_count=submissions.count(),
            last_contribution_at=last.occurred_at.isoformat() if last else None,
            raw_response={"mock": True},
        )

    def submit_contribution(self, rsa_pin: str, amount: Decimal, *, idempotency_key: str) -> SubmissionResult:
        simulate_latency()

        existing = MockPFASubmission.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return SubmissionResult(
                remittance_ref=existing.remittance_ref, status=existing.status, raw_response={"mock": True, "deduped": True}
            )

        maybe_raise(PFAProviderError, "Simulated PFA outage during contribution remittance")

        remittance_ref = f"MOCKREM-{uuid.uuid4().hex[:16].upper()}"
        MockPFASubmission.objects.create(
            rsa_pin=rsa_pin,
            idempotency_key=idempotency_key,
            remittance_ref=remittance_ref,
            amount=amount,
            status="successful",
            occurred_at=timezone.now(),
        )
        return SubmissionResult(
            remittance_ref=remittance_ref,
            status="successful",
            raw_response={"mock": True, "rsa_pin": rsa_pin, "amount": str(amount)},
        )
