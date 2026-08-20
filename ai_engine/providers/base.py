"""
AIProvider interface. Implementations must be pure from the caller's point
of view: given input, return structured JSON. No bank calls, no DB writes
(audit logging is done by ai_engine.services, not the provider itself) -
this boundary is what keeps the AI layer swappable and lets it be mocked/
stubbed for demos.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResult:
    parsed_output: dict[str, Any]
    raw_prompt: str
    raw_response: str
    model_name: str
    latency_ms: int
    fallback_used: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


class AIProviderError(Exception):
    """Raised for any provider-side failure (rate limit, network, bad output)."""


class AIProvider(ABC):
    @abstractmethod
    def classify_intent(self, *, message_text: str, context: dict) -> ProviderResult:
        """
        Returns parsed_output shaped like:
        {"intent": "approve" | "adjust" | "skip" | "balance_check" |
                    "show_dashboard" | "log_income" | "unknown",
         "confidence": 0.0-1.0, "entities": {...}}
        """

    @abstractmethod
    def generate_recommendation(self, *, income_context: dict) -> ProviderResult:
        """
        Returns parsed_output shaped like:
        {"suggested_amount": "1500.00", "reasoning": "...",
         "whatsapp_copy": "..."}
        `suggested_amount` is a total contribution amount only - the
        deterministic engine (pensions.services), not the AI, splits it
        between emergency and retirement using PensionPlan.emergency_ratio.
        """
