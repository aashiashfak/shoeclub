from django.contrib import admin


from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "username",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "updated_at",
    )

    search_fields = ("email", "username", "role")

    list_filter = ("role", "is_active", "is_staff", "is_superuser")

    ordering = ("-created_at",)


admin.site.register(CustomUser, CustomUserAdmin)
