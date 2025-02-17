from rest_framework import serializers
from .models import *


class UserAuthSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=False, min_length=6, max_length=6)

    def validate(self, attrs):
        request_type = self.context.get("request_type", "login")  

        if request_type == "verify":
            if "otp" not in attrs:
                raise serializers.ValidationError(
                    {"otp": "This field is required for OTP verification."}
                )
        return attrs


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(required=False)
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "username",
        ]

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        return user
