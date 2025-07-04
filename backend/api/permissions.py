from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Pozwala każdemu na odczyt, ale tylko adminom na zapis.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
