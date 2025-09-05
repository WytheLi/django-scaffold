from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_null=False)
    password = serializers.CharField(required=True, allow_null=False)


class VerificationCodeLoginSerializer(serializers.Serializer):

    mobile = serializers.CharField(min_length=11, max_length=11)
    code = serializers.CharField(min_length=6, max_length=6)
