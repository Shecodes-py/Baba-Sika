from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "full_name",
            "occupation_type",
            "onboarding_state",
            "preferred_language",
            "created_at",
        ]
        read_only_fields = fields
