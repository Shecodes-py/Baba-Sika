"""
The only public surface other apps should call into ai_engine through.
Functions here take plain input and return a structured dict - the one
side effect is writing the AIInteractionLog audit row (required for
financial-guidance auditability), which is intentionally NOT a bank/business
side effect: nothing here ever touches accounts.User's PIN, account_provisioning,
or pensions ledger state.

On any provider error (including Gemini rate limits), we transparently fall
back to StubProvider so a demo never hard-fails - the log row records
status="fallback_used" so it's visible in the audit trail.
"""

import logging

from .models import AIInteractionLog, AIInteractionStatus, AIInteractionType
from .providers import AIProviderError, get_ai_provider
from .providers.stub import StubProvider

logger = logging.getLogger(__name__)


def _run(*, user, interaction_type: str, input_context: dict, call):
    status = AIInteractionStatus.SUCCESS
    error_message = ""
    try:
        provider = get_ai_provider()
        result = call(provider)
    except AIProviderError as exc:
        logger.warning("AI provider failed (%s), falling back to stub: %s", interaction_type, exc)
        error_message = str(exc)
        try:
            result = call(StubProvider())
            status = AIInteractionStatus.FALLBACK_USED
        except AIProviderError as stub_exc:  # pragma: no cover - stub should never fail
            AIInteractionLog.objects.create(
                user=user,
                interaction_type=interaction_type,
                input_context=input_context,
                raw_prompt="",
                raw_response="",
                parsed_output={},
                model_name="",
                latency_ms=0,
                status=AIInteractionStatus.ERROR,
                error_message=f"{exc}; stub also failed: {stub_exc}",
            )
            raise

    log = AIInteractionLog.objects.create(
        user=user,
        interaction_type=interaction_type,
        input_context=input_context,
        raw_prompt=result.raw_prompt,
        raw_response=result.raw_response,
        parsed_output=result.parsed_output,
        model_name=result.model_name,
        latency_ms=result.latency_ms,
        status=status,
        error_message=error_message,
    )
    return result.parsed_output, log


def classify_intent(*, user, message_text: str, context: dict | None = None):
    """Returns (parsed_output: dict, log: AIInteractionLog)."""
    context = context or {}
    return _run(
        user=user,
        interaction_type=AIInteractionType.INTENT_CLASSIFICATION,
        input_context={"message_text": message_text, "context": context},
        call=lambda provider: provider.classify_intent(message_text=message_text, context=context),
    )


def generate_recommendation(*, user, income_context: dict):
    """Returns (parsed_output: dict, log: AIInteractionLog)."""
    return _run(
        user=user,
        interaction_type=AIInteractionType.RECOMMENDATION_GENERATION,
        input_context=income_context,
        call=lambda provider: provider.generate_recommendation(income_context=income_context),
    )
