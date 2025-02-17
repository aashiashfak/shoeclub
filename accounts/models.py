from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    ROLE_CHOICES = [
        ("Hospital", "Hospital Admin"),
        ("Admin", "Main Administator"),
    ]
    username = models.CharField(max_length=25, default="guest")
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    @property
    def tokens(self) -> dict[str, str]:
        print("reached in gen tokens")

        referesh = RefreshToken.for_user(self)

        return {
            "refresh": str(referesh),
            "access": str(referesh.access_token),
        }

    USERNAME_FIELD = "email"

    def __str__(self):
        return f"{self.username} ({self.role})"
