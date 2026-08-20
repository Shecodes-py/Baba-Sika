"""
Shared helpers for simulating a real external provider's behaviour (latency,
occasional outages) from MockWemaProvider and MockPFAProvider, so both the
onboarding flow and the confirm/execute flow genuinely have to handle a
failure path, not just the happy path.
"""

import random
import time

from django.conf import settings


def simulate_latency():
    low, high = settings.MOCK_PROVIDER_LATENCY_RANGE_MS
    time.sleep(random.uniform(low, high) / 1000)


def maybe_raise(error_cls, message: str, *, failure_rate: float | None = None):
    """Raises error_cls(message) with probability `failure_rate` (defaults to settings.MOCK_PROVIDER_FAILURE_RATE)."""
    rate = settings.MOCK_PROVIDER_FAILURE_RATE if failure_rate is None else failure_rate
    if random.random() < rate:
        raise error_cls(message)
