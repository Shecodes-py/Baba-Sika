"""
Deterministic canned-response provider. Used for local dev/demos and as an
automatic fallback when the real Gemini call errors or rate-limits (see
ai_engine.services), so a demo never dies on a 429.
"""

import time

from .base import AIProvider, ProviderResult


class StubProvider(AIProvider):
    def classify_intent(self, *, message_text: str, context: dict) -> ProviderResult:
        start = time.monotonic()
        text = (message_text or "").strip().lower()
        if text in {"1", "approve", "yes"}:
            intent = "approve"
        elif text in {"2", "adjust"}:
            intent = "adjust"
        elif text in {"3", "skip", "no"}:
            intent = "skip"
        elif "balance" in text or "progress" in text:
            intent = "balance_check"
        elif "dashboard" in text:
            intent = "show_dashboard"
        else:
            intent = "unknown"
        parsed = {"intent": intent, "confidence": 0.5, "entities": {}}
        latency_ms = int((time.monotonic() - start) * 1000)
        return ProviderResult(
            parsed_output=parsed,
            raw_prompt=f"[stub] classify_intent({message_text!r})",
            raw_response=str(parsed),
            model_name="stub-provider",
            latency_ms=latency_ms,
            fallback_used=True,
        )

    def generate_recommendation(self, *, income_context: dict) -> ProviderResult:
        start = time.monotonic()
        amount = income_context.get("amount")
        try:
            suggested = round(float(amount) * 0.15, 2) if amount else 500.0
        except (TypeError, ValueError):
            suggested = 500.0
        parsed = {
            "suggested_amount": f"{suggested:.2f}",
            "reasoning": "Stub recommendation: 15% of the logged income event.",
            "whatsapp_copy": (
                f"You just received income. BabaSika suggests setting aside "
                f"₦{suggested:,.2f} toward your pension today."
            ),
        }
        latency_ms = int((time.monotonic() - start) * 1000)
        return ProviderResult(
            parsed_output=parsed,
            raw_prompt=f"[stub] generate_recommendation({income_context!r})",
            raw_response=str(parsed),
            model_name="stub-provider",
            latency_ms=latency_ms,
            fallback_used=True,
        )
