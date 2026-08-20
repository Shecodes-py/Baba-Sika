"""
Deterministic bank operations. No AI, no conversation logic - just provider
(mock or, eventually, real) calls plus writing the results to our own
tables, with every call audited via ProviderCallLog.
"""

import time

from django.utils import timezone

from .models import (
    BankAccountLink,
    BankLinkStatus,
    BankTransactionMirror,
    ProviderCallLog,
    ProviderCallStatus,
    ProviderType,
)
from .providers import BankProviderError, get_bank_provider


def log_provider_call(
    *,
    provider_type: str,
    method_name: str,
    user=None,
    idempotency_key: str = "",
    request_payload: dict,
    response_payload: dict,
    status: str,
    error_message: str = "",
    latency_ms: int,
) -> ProviderCallLog:
    """
    Shared audit-log writer for BOTH BankProvider and PFAProvider calls -
    lives here (see account_provisioning.models.ProviderCallLog) so pensions
    can import it without creating a circular dependency.
    """
    return ProviderCallLog.objects.create(
        user=user,
        provider_type=provider_type,
        method_name=method_name,
        idempotency_key=idempotency_key,
        request_payload=request_payload,
        response_payload=response_payload,
        status=status,
        error_message=error_message,
        latency_ms=latency_ms,
    )


def link_account(user) -> BankAccountLink:
    link, _ = BankAccountLink.objects.get_or_create(user=user)
    if link.status == BankLinkStatus.LINKED and link.account_ref:
        return link  # already linked - never re-provision

    provider = get_bank_provider()
    start = time.monotonic()
    try:
        result = provider.create_account(user)
    except BankProviderError as exc:
        log_provider_call(
            provider_type=ProviderType.BANK,
            method_name="create_account",
            user=user,
            request_payload={"user_id": str(user.pk)},
            response_payload={},
            status=ProviderCallStatus.FAILED,
            error_message=str(exc),
            latency_ms=int((time.monotonic() - start) * 1000),
        )
        link.status = BankLinkStatus.FAILED
        link.save(update_fields=["status", "updated_at"])
        raise

    log_provider_call(
        provider_type=ProviderType.BANK,
        method_name="create_account",
        user=user,
        request_payload={"user_id": str(user.pk)},
        response_payload=result.raw_response,
        status=ProviderCallStatus.SUCCESS,
        latency_ms=int((time.monotonic() - start) * 1000),
    )

    link.account_ref = result.account_ref
    link.masked_account_number = result.masked_account_number
    link.link_raw_response = result.raw_response
    link.status = BankLinkStatus.LINKED
    link.save(
        update_fields=["account_ref", "masked_account_number", "link_raw_response", "status", "updated_at"]
    )
    return link


def sync_balance(user) -> BankAccountLink:
    link = BankAccountLink.objects.get(user=user)
    provider = get_bank_provider()
    result = provider.get_balance(link.account_ref)
    link.last_known_balance = result.available_balance
    link.last_balance_synced_at = timezone.now()
    link.save(update_fields=["last_known_balance", "last_balance_synced_at", "updated_at"])
    return link


def sync_transaction_history(user, since: str | None = None) -> list[BankTransactionMirror]:
    link = BankAccountLink.objects.get(user=user)
    provider = get_bank_provider()
    records = provider.get_transaction_history(link.account_ref, since=since)
    mirrored = []
    for record in records:
        obj, _ = BankTransactionMirror.objects.update_or_create(
            transaction_ref=record.transaction_ref,
            defaults={
                "user": user,
                "amount": record.amount,
                "direction": record.direction,
                "narration": record.narration,
                "occurred_at": record.occurred_at,
                "raw_payload": record.raw_response,
            },
        )
        mirrored.append(obj)
    return mirrored


def transfer_funds(*, user, amount, purpose: str, idempotency_key: str):
    """
    The one place pensions.services calls to move money. Wraps
    BankProvider.initiate_transfer with audit logging; raises BankProviderError
    on failure (simulated outage or insufficient funds) - callers handle that.
    """
    link = BankAccountLink.objects.get(user=user)
    provider = get_bank_provider()
    request_payload = {"account_ref": link.account_ref, "amount": str(amount), "purpose": purpose}
    start = time.monotonic()
    try:
        result = provider.initiate_transfer(
            link.account_ref, amount, purpose, idempotency_key=idempotency_key
        )
    except BankProviderError as exc:
        log_provider_call(
            provider_type=ProviderType.BANK,
            method_name="initiate_transfer",
            user=user,
            idempotency_key=idempotency_key,
            request_payload=request_payload,
            response_payload={},
            status=ProviderCallStatus.FAILED,
            error_message=str(exc),
            latency_ms=int((time.monotonic() - start) * 1000),
        )
        raise

    log_provider_call(
        provider_type=ProviderType.BANK,
        method_name="initiate_transfer",
        user=user,
        idempotency_key=idempotency_key,
        request_payload=request_payload,
        response_payload=result.raw_response,
        status=ProviderCallStatus.SUCCESS,
        latency_ms=int((time.monotonic() - start) * 1000),
    )
    return result
