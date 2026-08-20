from rest_framework import serializers

from .models import Contribution


class RetirementReadinessSerializer(serializers.Serializer):
    score = serializers.FloatField()
    label = serializers.CharField()
    basis = serializers.CharField()


class ProgressSummarySerializer(serializers.Serializer):
    emergency_fund_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    emergency_fund_target = serializers.DecimalField(
        max_digits=14, decimal_places=2, allow_null=True
    )
    retirement_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    retirement_readiness = RetirementReadinessSerializer()
    bank_account_balance = serializers.DecimalField(
        max_digits=14, decimal_places=2, allow_null=True
    )
    emergency_ratio = serializers.DecimalField(max_digits=4, decimal_places=2)
    preferred_pfa = serializers.CharField(allow_blank=True)
    pfa_registration_status = serializers.CharField()
    rsa_pin = serializers.CharField(allow_blank=True)


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = ["id", "amount", "destination", "status", "executed_at", "created_at"]
        read_only_fields = fields
