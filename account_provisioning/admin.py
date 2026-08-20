from django.contrib import admin

from .models import BankAccountLink, BankTransactionMirror, ProviderCallLog


@admin.register(BankAccountLink)
class BankAccountLinkAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "account_ref", "last_known_balance", "last_balance_synced_at"]
    list_filter = ["status"]
    search_fields = ["user__phone_number", "account_ref"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(BankTransactionMirror)
class BankTransactionMirrorAdmin(admin.ModelAdmin):
    list_display = ["user", "direction", "amount", "narration", "occurred_at"]
    list_filter = ["direction"]
    search_fields = ["user__phone_number", "transaction_ref"]
    readonly_fields = ["id", "synced_at"]


@admin.register(ProviderCallLog)
class ProviderCallLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "provider_type", "method_name", "status", "latency_ms"]
    list_filter = ["provider_type", "method_name", "status"]
    search_fields = ["user__phone_number", "idempotency_key"]
    readonly_fields = [f.name for f in ProviderCallLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
