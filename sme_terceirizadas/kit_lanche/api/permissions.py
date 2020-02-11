from rest_framework import permissions


class SolicitacaoUnificadaPermission(permissions.BasePermission):
    message = 'O seu perfil não tem permissao para bla bla bla'

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class PodeIniciarSolicitacaoUnificadaPermission(permissions.BasePermission):
    message = 'Você não tem permissão para iniciar um pedido de solicitação unificada.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de iniciar o pedido de solicitacao unificada
        # entende-se que ele responde pela escola
        return True
