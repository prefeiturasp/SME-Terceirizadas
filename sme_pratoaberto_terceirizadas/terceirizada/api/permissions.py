from rest_framework import permissions


class PodeAlterarTerceirizadasPermission(permissions.BasePermission):
    message = 'O seu perfil não tem permissao para alterar terceirizadas'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True
