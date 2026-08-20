from django.conf import settings
from django.utils.module_loading import import_string

from .base import AIProvider, AIProviderError, ProviderResult

__all__ = ["AIProvider", "AIProviderError", "ProviderResult", "get_ai_provider"]

_instance = None


def get_ai_provider() -> AIProvider:
    """
    Returns the configured AIProvider singleton, per settings.AI_PROVIDER_BACKEND.
    Swap Gemini for the stub (rate limits during a demo, no API key, etc.)
    purely via settings/env - no call site should import GeminiProvider directly.
    """
    global _instance
    if _instance is None:
        provider_class = import_string(settings.AI_PROVIDER_BACKEND)
        _instance = provider_class()
    return _instance
