from rest_framework import serializers


class VerifyMagicLinkRequestSerializer(serializers.Serializer):
    token = serializers.CharField()


class VerifyMagicLinkResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
