from rest_framework import permissions


class SolicitacaoUnificadaPermission(permissions.BasePermission):
    message = 'O seu perfil não tem permissao para bla bla bla'

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False
