from django.contrib import admin

from .models import AIInteractionLog


@admin.register(AIInteractionLog)
class AIInteractionLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "interaction_type", "status", "model_name", "latency_ms"]
    list_filter = ["interaction_type", "status", "model_name"]
    search_fields = ["user__phone_number"]
    readonly_fields = [f.name for f in AIInteractionLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
