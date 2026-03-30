from rest_framework import permissions


class IsVendor(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'vendor' role
    to create or edit resources.
    """
    def has_permission(self, request, view):
        # Anyone can "GET" (view) the list
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only users with the 'vendor' role can "POST" (create)
        return bool(request.user and
                    request.user.is_authenticated and
                    request.user.profile.role == 'vendor')
