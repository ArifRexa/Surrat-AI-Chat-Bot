from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class HasActiveSubscription(BasePermission):
    def has_permission(self, request, view):
        user_subscription = getattr(request.user, "usersubscription", None)

        if user_subscription and user_subscription.is_active:
            return True

        raise PermissionDenied(
            "Your subscription has expired. Please renew to continue accessing this service."
        )
