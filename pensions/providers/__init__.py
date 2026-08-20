from django.conf import settings
from django.utils.module_loading import import_string

from .base import ContributionStatusResult, PFAProvider, PFAProviderError, RegistrationResult, SubmissionResult

__all__ = [
    "ContributionStatusResult",
    "PFAProvider",
    "PFAProviderError",
    "RegistrationResult",
    "SubmissionResult",
    "get_pfa_provider",
]

_instance = None


def get_pfa_provider() -> PFAProvider:
    """Returns the configured PFAProvider singleton, per settings.PFA_PROVIDER_BACKEND."""
    global _instance
    if _instance is None:
        provider_class = import_string(settings.PFA_PROVIDER_BACKEND)
        _instance = provider_class()
    return _instance
