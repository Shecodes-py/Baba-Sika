from django.contrib import admin

from .models import MagicLinkToken


@admin.register(MagicLinkToken)
class MagicLinkTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "requested_via", "expires_at", "used_at"]
    list_filter = ["status", "requested_via"]
    search_fields = ["user__phone_number", "jti"]
    readonly_fields = [f.name for f in MagicLinkToken._meta.fields]

    def has_add_permission(self, request):
        return False
