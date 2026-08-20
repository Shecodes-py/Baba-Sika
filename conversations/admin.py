from django.contrib import admin

from .models import ConversationSession, MessageLog


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "state", "last_interaction_at"]
    list_filter = ["state"]
    search_fields = ["user__phone_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ["user", "direction", "message_type", "processed", "created_at"]
    list_filter = ["direction", "message_type", "processed"]
    search_fields = ["user__phone_number", "twilio_message_sid"]
    readonly_fields = [f.name for f in MessageLog._meta.fields]

    def has_add_permission(self, request):
        return False
