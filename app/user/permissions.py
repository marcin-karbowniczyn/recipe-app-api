from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    message = 'You cannot perform this action'

    def has_permission(self, request, view):
        return request.user.is_superuser
