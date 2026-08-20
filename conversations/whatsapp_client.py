"""
Thin wrapper around the Twilio WhatsApp Business API. Every other module
sends outbound WhatsApp messages through conversations.services.send_message
(which logs to MessageLog), not through this client directly.
"""

import logging

from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)

_client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return _client


def send_whatsapp_text(*, to_phone_number: str, body: str) -> str:
    """Sends a freeform WhatsApp text message. Returns the Twilio message SID."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio not configured - skipping outbound send to %s: %s", to_phone_number, body)
        return ""
    message = _get_client().messages.create(
        from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{to_phone_number}",
        body=body,
    )
    return message.sid
