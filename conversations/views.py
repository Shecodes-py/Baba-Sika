import logging

from django.conf import settings
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from twilio.request_validator import RequestValidator

from .flows.router import dispatch
from .services import get_or_create_session, get_or_create_user, log_inbound_message, mark_processed

logger = logging.getLogger(__name__)

_EMPTY_TWIML = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'


class TwilioWhatsAppWebhookView(APIView):
    """
    POST /api/conversations/webhook/whatsapp/ - Twilio's inbound WhatsApp
    webhook. Processed synchronously (not via Celery) specifically so a
    transaction PIN reply never has to transit the message broker - see
    conversations.flows.router for the rationale. Twilio's webhook timeout
    is generous (15s) so this is safe for the DB-bound work each flow does.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if not self._is_valid_signature(request):
            logger.warning("Rejected Twilio webhook with invalid signature")
            return HttpResponse(status=403)

        message_sid = request.data.get("MessageSid", "")
        from_number = request.data.get("From", "")
        body = request.data.get("Body", "")

        if not message_sid or not from_number:
            return HttpResponse(status=400)

        user = get_or_create_user(from_number)
        session = get_or_create_session(user)

        message_log, created = log_inbound_message(
            user=user,
            session=session,
            twilio_message_sid=message_sid,
            body=body,
            raw_payload=dict(request.data.items()) if hasattr(request.data, "items") else dict(request.data),
        )
        if not created:
            # Twilio retried a delivery we've already processed - no-op.
            return HttpResponse(_EMPTY_TWIML, content_type="text/xml")

        dispatch(user=user, session=session, message_log=message_log, raw_body=body)
        mark_processed(message_log)

        return HttpResponse(_EMPTY_TWIML, content_type="text/xml")

    @staticmethod
    def _is_valid_signature(request) -> bool:
        auth_token = settings.TWILIO_AUTH_TOKEN
        if not auth_token:
            if settings.DEBUG:
                return True
            logger.error("TWILIO_AUTH_TOKEN not configured - refusing unverified webhook")
            return False

        signature = request.META.get("HTTP_X_TWILIO_SIGNATURE", "")
        url = request.build_absolute_uri()
        validator = RequestValidator(auth_token)
        return validator.validate(url, request.POST, signature)
