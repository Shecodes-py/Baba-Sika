import json
import time

from django.conf import settings

from .base import AIProvider, AIProviderError, ProviderResult

INTENT_PROMPT = """You are classifying a reply inside a WhatsApp pension-savings \
conversation for BabaSika, a product for Nigerian informal workers.
The user was shown a numbered menu. Classify their reply into exactly one \
intent from: approve, adjust, skip, balance_check, show_dashboard, log_income, unknown.
Conversation context (JSON): {context}
User's message: "{message_text}"

Respond with ONLY minified JSON, no prose, no markdown fences, shaped exactly like:
{{"intent": "<one of the allowed values>", "confidence": <0.0-1.0>, "entities": {{}}}}
"""

RECOMMENDATION_PROMPT = """You are BabaSika, an AI that drafts a pension \
contribution recommendation for a Nigerian informal-sector worker after they \
receive income. You NEVER move money yourself - you only propose a total \
amount and write a short, warm, WhatsApp-appropriate message in simple English \
(and Nigerian Pidgin flavor is welcome, but keep it clear).
Income event (JSON): {income_context}

Respond with ONLY minified JSON, no prose, no markdown fences, shaped exactly like:
{{"suggested_amount": "<decimal string, Naira, no currency symbol>", \
"reasoning": "<one sentence, for the audit log, not shown to the user>", \
"whatsapp_copy": "<the message to send the user, under 300 characters>"}}
"""


class GeminiProvider(AIProvider):
    def __init__(self):
        from google import genai  # deferred import so the app still boots without the SDK installed

        if not settings.GEMINI_API_KEY:
            raise AIProviderError("GEMINI_API_KEY is not configured")
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model_name = settings.GEMINI_MODEL_NAME

    def _generate(self, prompt: str) -> tuple[str, int]:
        start = time.monotonic()
        try:
            response = self._client.models.generate_content(
                model=self._model_name, contents=prompt
            )
        except Exception as exc:  # noqa: BLE001 - any SDK/network error becomes AIProviderError
            raise AIProviderError(f"Gemini call failed: {exc}") from exc
        latency_ms = int((time.monotonic() - start) * 1000)
        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise AIProviderError("Gemini returned an empty response")
        return text, latency_ms

    @staticmethod
    def _parse_json(raw_response: str) -> dict:
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise AIProviderError(f"Gemini did not return valid JSON: {exc}") from exc

    def classify_intent(self, *, message_text: str, context: dict) -> ProviderResult:
        prompt = INTENT_PROMPT.format(
            context=json.dumps(context, default=str), message_text=message_text
        )
        raw_response, latency_ms = self._generate(prompt)
        parsed = self._parse_json(raw_response)
        return ProviderResult(
            parsed_output=parsed,
            raw_prompt=prompt,
            raw_response=raw_response,
            model_name=self._model_name,
            latency_ms=latency_ms,
        )

    def generate_recommendation(self, *, income_context: dict) -> ProviderResult:
        prompt = RECOMMENDATION_PROMPT.format(
            income_context=json.dumps(income_context, default=str)
        )
        raw_response, latency_ms = self._generate(prompt)
        parsed = self._parse_json(raw_response)
        return ProviderResult(
            parsed_output=parsed,
            raw_prompt=prompt,
            raw_response=raw_response,
            model_name=self._model_name,
            latency_ms=latency_ms,
        )
