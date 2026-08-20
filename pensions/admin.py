from django.contrib import admin

from .models import (
    Contribution,
    ContributionSchedule,
    EmergencyFund,
    MockPFARegistration,
    MockPFASubmission,
    PendingAction,
    PensionPlan,
    RetirementTracker,
)


@admin.register(PensionPlan)
class PensionPlanAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "status",
        "emergency_ratio",
        "retirement_target_age",
        "preferred_pfa",
        "pfa_registration_status",
        "rsa_pin",
    ]
    list_filter = ["pfa_registration_status", "preferred_pfa"]
    search_fields = ["user__phone_number", "rsa_pin"]
    readonly_fields = ["id", "rsa_pin", "pfa_registration_status", "pfa_registered_at", "created_at", "updated_at"]


@admin.register(ContributionSchedule)
class ContributionScheduleAdmin(admin.ModelAdmin):
    list_display = ["plan", "frequency", "is_active"]
    list_filter = ["frequency", "is_active"]


@admin.register(PendingAction)
class PendingActionAdmin(admin.ModelAdmin):
    list_display = ["user", "action_type", "status", "expires_at", "confirmed_at", "created_at"]
    list_filter = ["status", "action_type"]
    search_fields = ["user__phone_number", "idempotency_key"]
    readonly_fields = ["id", "idempotency_key", "created_at", "updated_at"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ["plan", "destination", "amount", "status", "executed_at"]
    list_filter = ["destination", "status"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EmergencyFund)
class EmergencyFundAdmin(admin.ModelAdmin):
    list_display = ["plan", "current_balance", "target_amount"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(RetirementTracker)
class RetirementTrackerAdmin(admin.ModelAdmin):
    list_display = ["plan", "current_balance", "readiness_score", "readiness_label"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(MockPFARegistration)
class MockPFARegistrationAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "rsa_pin", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__phone_number", "rsa_pin", "idempotency_key"]
    readonly_fields = [f.name for f in MockPFARegistration._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(MockPFASubmission)
class MockPFASubmissionAdmin(admin.ModelAdmin):
    list_display = ["rsa_pin", "amount", "status", "occurred_at"]
    search_fields = ["rsa_pin", "remittance_ref", "idempotency_key"]
    readonly_fields = [f.name for f in MockPFASubmission._meta.fields]

    def has_add_permission(self, request):
        return False
