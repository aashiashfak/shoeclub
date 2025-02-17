from .serializers import *
from rest_framework.views import APIView
from utils.utils import generate_otp, send_otp_email
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status, generics
from .models import CustomUser
from django.conf import settings
from upstash_redis import Redis
from decouple import config

redis = Redis(
    url="https://accepted-mantis-42257.upstash.io",
    token=config('REDIS_TOKEN'),
)


class UserLoginRequestAPIView(APIView):
    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            cache_key = f"otp_{email}"
            existing_otp = redis.get(cache_key)

            if not existing_otp:
                otp = generate_otp()
                redis.set(cache_key, otp, ex=120)
            else:
                otp = existing_otp
            username = email.split("@")[0]

            print("generated_otp", otp)
            try:
                send_otp_email(email, username, otp)
                return Response(
                    {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
                )
            except Exception as e:
                redis.delete(cache_key)
                return Response(
                    {"error": "Failed to send OTP. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginVerifyAPIView(APIView):
    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            stored_otp = redis.get(f"otp_{email}")
            print(stored_otp)

            if stored_otp == otp:
                try:
                    user = CustomUser.objects.get(email=email)
                except CustomUser.DoesNotExist:
                    redis.delete(f"otp_{email}")
                    return Response(
                        {"error": "User does not exist."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                redis.delete(f"otp_{email}")

                tokens = user.tokens
                user_serializer = UserSerializer(user)

                response = Response(
                    {
                        "message": "User verified successfully.",
                        "user": user_serializer.data,
                        "access": tokens["access"],
                    },
                    status=status.HTTP_200_OK,
                )

                print(response.data)

                refresh_token_expiry = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

                response.set_cookie(
                    key="refresh",
                    value=tokens["refresh"],
                    httponly=True,
                    secure=False,
                    samesite="Lax",
                    max_age=int(refresh_token_expiry.total_seconds()),
                )

                return response
            return Response(
                {"error": "Invalid OTP or Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
