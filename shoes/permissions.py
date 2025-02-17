from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only admins for unsafe methods (POST, PUT, DELETE).
    Safe methods (GET, HEAD, OPTIONS) are allowed for everyone.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            getattr(request.user, "role", None) == "Admin" or request.user.is_staff
        )
