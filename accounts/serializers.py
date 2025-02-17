from rest_framework import serializers
from .models import *


class UserAuthSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=False, min_length=6, max_length=6)
    role = serializers.CharField(required=False, max_length=15)

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
