from django.conf import settings
from django.db import models

from babasika.base_models import TimeStampedModel, UUIDPrimaryKeyModel


class ConversationState(models.TextChoices):
    ONBOARDING_GREETING = "onboarding_greeting", "Onboarding: greeting"
    ONBOARDING_LANGUAGE = "onboarding_language", "Onboarding: language selection"
    ONBOARDING_OCCUPATION = "onboarding_occupation", "Onboarding: occupation"
    ONBOARDING_BANK_LINK = "onboarding_bank_link", "Onboarding: bank link"
    ONBOARDING_PFA_SELECTION = "onboarding_pfa_selection", "Onboarding: PFA selection"
    ONBOARDING_PFA_LINK = "onboarding_pfa_link", "Onboarding: existing RSA PIN or new"
    ONBOARDING_CONSENT = "onboarding_consent", "Onboarding: consent"
    ONBOARDING_PIN_SETUP = "onboarding_pin_setup", "Onboarding: PIN setup"
    IDLE = "idle", "Idle"
    AWAITING_CONFIRMATION = "awaiting_confirmation", "Awaiting confirmation"
    AWAITING_PIN = "awaiting_pin", "Awaiting PIN"
    EXPIRED = "expired", "Expired"


class ConversationSession(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    Moment-to-moment dialogue state - distinct from accounts.User.onboarding_state,
    which is the longer-lived cross-session milestone. One active session per
    user; `context` carries scratch data for whatever step is in flight
    (e.g. which PendingAction we're awaiting a PIN for).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversation_session"
    )
    state = models.CharField(
        max_length=25, choices=ConversationState.choices, default=ConversationState.ONBOARDING_GREETING
    )
    context = models.JSONField(default=dict, blank=True)
    last_interaction_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.state}"


class MessageDirection(models.TextChoices):
    INBOUND = "inbound", "Inbound"
    OUTBOUND = "outbound", "Outbound"


class MessageType(models.TextChoices):
    TEXT = "text", "Text"
    INTERACTIVE_REPLY = "interactive_reply", "Interactive reply"
    TEMPLATE = "template", "Template"
    MEDIA = "media", "Media"


class MessageLog(UUIDPrimaryKeyModel, TimeStampedModel):
    """
    Every inbound/outbound WhatsApp message. `twilio_message_sid` is unique
    so the inbound webhook can dedupe retried deliveries (Twilio may resend
    on a slow/failed response). `body` is redacted for messages exchanged
    while a transaction PIN was in flight - see conversations.services.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )
    session = models.ForeignKey(
        ConversationSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages"
    )
    direction = models.CharField(max_length=10, choices=MessageDirection.choices)
    twilio_message_sid = models.CharField(max_length=64, unique=True, null=True, blank=True)
    body = models.TextField(blank=True)
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    raw_payload = models.JSONField(default=dict, blank=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]

    def __str__(self):
        return f"{self.direction} - {self.user} @ {self.created_at}"
