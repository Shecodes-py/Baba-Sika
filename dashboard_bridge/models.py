from django.conf import settings
from django.db import models

from babasika.base_models import TimeStampedModel, UUIDPrimaryKeyModel


class MagicLinkStatus(models.TextChoices):
    ISSUED = "issued", "Issued"
    USED = "used", "Used"
    EXPIRED = "expired", "Expired"


class MagicLinkRequestSource(models.TextChoices):
    ONBOARDING_COMPLETE = "onboarding_complete", "Onboarding complete"
    ON_DEMAND = "on_demand", "On demand"


class MagicLinkToken(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    Audit/single-use record for a minted MagicLinkToken JWT. The raw JWT is
    never stored - only its jti, so we can enforce single-use and expiry
    cleanup without being able to reconstruct the token from the DB.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="magic_link_tokens"
    )
    jti = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=10, choices=MagicLinkStatus.choices, default=MagicLinkStatus.ISSUED)
    requested_via = models.CharField(max_length=25, choices=MagicLinkRequestSource.choices)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.status} ({self.jti})"
