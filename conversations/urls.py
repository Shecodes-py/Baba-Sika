from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import TwilioWhatsAppWebhookView

app_name = "conversations"

urlpatterns = [
    path("webhook/whatsapp/", csrf_exempt(TwilioWhatsAppWebhookView.as_view()), name="whatsapp-webhook"),
]
