from django.conf import settings
from django.db import models

from babasika.base_models import TimeStampedModel, UUIDPrimaryKeyModel


class AIInteractionType(models.TextChoices):
    INTENT_CLASSIFICATION = "intent_classification", "Intent classification"
    RECOMMENDATION_GENERATION = "recommendation_generation", "Recommendation generation"


class AIInteractionStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    ERROR = "error", "Error"
    FALLBACK_USED = "fallback_used", "Fallback used"


class AIInteractionLog(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    Full audit trail for every AI call - this is financial guidance, so raw
    prompt/response are always kept, even on error/fallback. Never mutated
    after creation.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_interactions",
    )
    interaction_type = models.CharField(max_length=30, choices=AIInteractionType.choices)
    input_context = models.JSONField(default=dict, blank=True)
    raw_prompt = models.TextField(blank=True)
    raw_response = models.TextField(blank=True)
    parsed_output = models.JSONField(default=dict, blank=True)
    model_name = models.CharField(max_length=50, blank=True)
    latency_ms = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=15, choices=AIInteractionStatus.choices)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.interaction_type} - {self.user} @ {self.created_at}"
