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
from rest_framework_simplejwt.views import TokenRefreshView

redis = Redis(
    url="https://accepted-mantis-42257.upstash.io",
    token=config("REDIS_TOKEN"),
)


class UserLoginRequestAPIView(APIView):
    """
    Handles the OTP request during user login.
    Generates or retrieves an OTP for the user based on the email provided in the request,
    then sends the OTP via email to the user.
    """

    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            cache_key = f"otp_{email}"
            existing_otp = redis.get(cache_key)

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                redis.delete(cache_key)
                return Response(
                    {"error": "User does not exist. pls signUp"},
                    status=status.HTTP_404_NOT_FOUND,
                )

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
    """
    Verifies the OTP entered by the user during login.
    If the OTP matches the stored value, the user is authenticated,
    and a JWT access token is generated and returned in the response.
    """

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


class UserSignUpRequestView(APIView):
    """
    Handles the OTP request during user signup.
    Generates or retrieves an OTP for the user based on the email provided in the request,
    then sends the OTP via email to the user.
    """

    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            if CustomUser.objects.filter(email=email).exists():
                return Response(
                    {"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST
                )

            cache_key = f"otp_{email}"
            otp = cache.get(cache_key) or generate_otp()
            cache.set(cache_key, otp, timeout=120)

            print("generated_otp", otp)

            username = email.split("@")[0]

            try:
                send_otp_email(email, username, otp)
                return Response(
                    {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
                )
            except Exception:
                cache.delete(cache_key)
                return Response(
                    {"error": "Failed to send OTP. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSignUpVerifyView(APIView):
    """
    Verifies the OTP entered by the user during signup.
    If the OTP matches the stored value and no user with the given email exists,
    a new user is created, and a JWT access token is generated and returned in the response.
    """

    def post(self, request):
        print("user_data", request.data)
        serializer = UserAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        role = serializer.validated_data["role"]

        stored_otp = cache.get(f"otp_{email}")
        print("stored_otp", stored_otp, "otp", otp, end="\n")

        if otp != stored_otp:
            return Response(
                {"error": "Invalid OTP!"}, status=status.HTTP_400_BAD_REQUEST
            )

        cache.delete(f"otp_{email}")

        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user:
            return Response(
                {"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = CustomUser.objects.create_user(email=email, password=None, role=role)
        if not user:
            return Response(
                {"message": "User creation failed"}, status=status.HTTP_400_BAD_REQUEST
            )

        tokens = user.tokens
        user_serializer = UserSerializer(user)

        response = Response(
            {
                "message": "OTP verified and user signed in successfully!",
                "user": user_serializer.data,
                "access": tokens["access"],
            },
            status=status.HTTP_200_OK,
        )

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


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom TokenRefreshView that checks for refresh_token in cookies.
    """

    def post(self, request, *args, **kwargs):

        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["refresh"] = refresh_token

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    API View for logging out the user by deleting the refresh token cookie.
    """

    def post(self, request):
        response = Response(
            {"detail": "Logged out successfully."}, status=status.HTTP_200_OK
        )
        response.delete_cookie("refresh")
        return response
