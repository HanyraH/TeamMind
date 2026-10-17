"""Permissions for role-based access control."""
from rest_framework.permissions import BasePermission
from .models import UserRole


class IsAdminRole(BasePermission):
    """Allow access only to admins."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and (request.user.role == UserRole.ADMIN or request.user.is_superuser))


class IsProjectManagerOrAdmin(BasePermission):
    """Allow access to project managers and admins."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER])


class IsOwnerOrAdmin(BasePermission):
    """Allow owner or admin to modify their own objects."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN:
            return True
        # Check if obj has user or employee field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'employee') and hasattr(obj.employee, 'user'):
            return obj.employee.user == request.user
        return False
