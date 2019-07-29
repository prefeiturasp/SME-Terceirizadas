from rest_framework import permissions


class PodeMarcarComoLidaPermission(permissions.BasePermission):
    message = 'Você não tem permissão para marcar como lida.'

    def has_object_permission(self, request, view, notification):
        return request.user == notification.recipient
