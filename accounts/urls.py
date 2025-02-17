from django.urls import path
from .views import *


urlpatterns = [
    path("sign-in/", UserLoginRequestAPIView.as_view(), name="user_sign_in"),
    path("verify-otp/", UserLoginVerifyAPIView.as_view(), name="verify_otp"),
    path("sign-up/", UserSignUpRequestView.as_view(), name="user_sign_up"),
    path("sign-up/verify-otp/", UserSignUpVerifyView.as_view(), name="sign_up_verify_otp"),
]
