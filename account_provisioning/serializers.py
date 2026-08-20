from rest_framework import serializers

from .models import BankAccountLink, BankTransactionMirror


class BankAccountLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccountLink
        fields = ["status", "masked_account_number", "last_known_balance", "last_balance_synced_at"]
        read_only_fields = fields


class BankTransactionMirrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransactionMirror
        fields = ["amount", "direction", "narration", "occurred_at"]
        read_only_fields = fields
