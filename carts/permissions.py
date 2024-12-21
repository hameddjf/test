from rest_framework import permissions


class IsCartOwner(permissions.BasePermission):
    """Permission check for cart item ownership"""

    def has_permission(self, request, view):
        # Allow access to the list only for logged in users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPromotionAdmin(permissions.BasePermission):
    """Permission check for promotion management"""

    def has_permission(self, request, view):
        # Only admins can manage promotions
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff
