from django.conf import settings
from django.utils.module_loading import import_string

from .base import (
    AccountResult,
    BalanceResult,
    BankProvider,
    BankProviderError,
    TransactionRecord,
    TransferResult,
)

__all__ = [
    "AccountResult",
    "BalanceResult",
    "BankProvider",
    "BankProviderError",
    "TransactionRecord",
    "TransferResult",
    "get_bank_provider",
]

_instance = None


def get_bank_provider() -> BankProvider:
    """
    Returns the configured BankProvider singleton, per settings.BANK_PROVIDER_BACKEND
    (defaults to MockWemaProvider - see that module's docstring for why).
    """
    global _instance
    if _instance is None:
        provider_class = import_string(settings.BANK_PROVIDER_BACKEND)
        _instance = provider_class()
    return _instance
