from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .models import MagicLinkStatus, MagicLinkToken
from .tokens import MAGIC_LINK_PURPOSE_CLAIM, MAGIC_LINK_PURPOSE_VALUE, MagicLinkToken as MagicLinkJWT


class MagicLinkError(Exception):
    pass


class MagicLinkExpiredError(MagicLinkError):
    pass


class MagicLinkAlreadyUsedError(MagicLinkError):
    pass


class MagicLinkInvalidError(MagicLinkError):
    pass


def issue_magic_link(user, *, requested_via: str) -> tuple[str, str]:
    """
    Mints a single-use, ~15 min JWT and returns (dashboard_url, raw_jwt).
    Called after onboarding completes, or on-demand from "show my dashboard".
    """
    token = MagicLinkJWT()
    token["user_id"] = str(user.pk)

    MagicLinkToken.objects.create(
        user=user,
        jti=token["jti"],
        requested_via=requested_via,
        expires_at=timezone.now() + token.lifetime,
    )

    raw_jwt = str(token)
    # FLAG: DASHBOARD_BASE_URL is a placeholder until the dashboard's real
    # deployed URL and expected query param name are confirmed.
    dashboard_url = f"{settings.DASHBOARD_BASE_URL.rstrip('/')}/auth?token={raw_jwt}"
    return dashboard_url, raw_jwt


def verify_and_exchange(raw_jwt: str) -> str:
    """
    Called by the dashboard's POST /verify/ hit. Validates signature/expiry
    via SimpleJWT, enforces single-use via MagicLinkToken.status, and
    returns a normal session AccessToken (SIMPLE_JWT's default lifetime)
    for the dashboard to use as a Bearer token on subsequent API calls.
    """
    try:
        token = MagicLinkJWT(raw_jwt)
    except TokenError as exc:
        raise MagicLinkInvalidError(str(exc)) from exc

    if token.get(MAGIC_LINK_PURPOSE_CLAIM) != MAGIC_LINK_PURPOSE_VALUE:
        raise MagicLinkInvalidError("Token is not a dashboard magic link")

    try:
        record = MagicLinkToken.objects.select_related("user").get(jti=token["jti"])
    except MagicLinkToken.DoesNotExist:
        raise MagicLinkInvalidError("Unknown token") from None

    if record.status == MagicLinkStatus.USED:
        raise MagicLinkAlreadyUsedError("Magic link already used")
    if record.status == MagicLinkStatus.EXPIRED or record.expires_at <= timezone.now():
        record.status = MagicLinkStatus.EXPIRED
        record.save(update_fields=["status", "updated_at"])
        raise MagicLinkExpiredError("Magic link expired")

    record.status = MagicLinkStatus.USED
    record.used_at = timezone.now()
    record.save(update_fields=["status", "used_at", "updated_at"])

    session_token = AccessToken()
    session_token["user_id"] = str(record.user.pk)
    return str(session_token)
