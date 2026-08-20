from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import ConsentRecord, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-created_at"]
    list_display = [
        "phone_number",
        "full_name",
        "occupation_type",
        "onboarding_state",
        "is_active",
        "is_staff",
        "created_at",
    ]
    list_filter = ["onboarding_state", "occupation_type", "is_active", "is_staff"]
    search_fields = ["phone_number", "full_name"]
    readonly_fields = [
        "id",
        "transaction_pin_hash",
        "pin_attempt_count",
        "pin_locked_until",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (None, {"fields": ("id", "phone_number", "password")}),
        (
            "Profile",
            {"fields": ("full_name", "occupation_type", "preferred_language")},
        ),
        ("Onboarding", {"fields": ("onboarding_state",)}),
        (
            "Transaction PIN",
            {"fields": ("transaction_pin_hash", "pin_attempt_count", "pin_locked_until")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ["user", "consent_type", "channel", "accepted_at"]
    list_filter = ["consent_type", "channel"]
    search_fields = ["user__phone_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
