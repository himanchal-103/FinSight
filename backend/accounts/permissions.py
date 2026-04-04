from rest_framework.permissions import BasePermission


class IsViewer(BasePermission):
    """
    Viewer, Analyst, Admin — any authenticated user
    """
    message = "Authentication required"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAnalyst(BasePermission):
    """
    Analyst and Admin only
    """
    message = "Analyst or Admin access required"

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in ("analyst", "admin")


class IsAdminRole(BasePermission):
    """
    Admin only
    """
    message = "Admin access required"

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role == "admin"