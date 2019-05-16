from rest_framework import permissions
from .models import Permission, ProfilePermission
from django.core.exceptions import ObjectDoesNotExist


class ValidatePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if (self._valid_profile_and_permission(request)):
            return True

        return False

    def _valid_profile_and_permission(self, request):
        try:
            endpoint = request.get_full_path()

            profile = request.user.profile

            permission = Permission.objects.get(endpoint=endpoint).id

            granted_permission = ProfilePermission.objects.filter(profile=profile, permission=permission)

            granted_action = self._valida_request_reader_or_writer(request.method, granted_permission.get().verbs)

            if granted_permission:
                return granted_action

            return False

        except ObjectDoesNotExist:
            return False

    def _valida_request_reader_or_writer(self, method, verb):
        if method in permissions.SAFE_METHODS and verb == 'R':
            return True
        elif verb == 'W':
            return True

        return False
