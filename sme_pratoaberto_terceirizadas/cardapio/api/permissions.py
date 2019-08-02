from rest_framework import permissions


class PodeIniciarAlteracaoCardapioPermission(permissions.BasePermission):
    message = 'Você não tem permissão para iniciar um pedido de alteração de cardápio.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de iniciar o pedido de alteração de cardápio
        # entende-se que ele responde pela escola
        return True


class PodeAprovarAlteracaoCardapioPermission(permissions.BasePermission):
    message = 'Você não tem permissão para aprovar um pedido de alteração de cardápio.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de
        # aprovar da escola o pedido de alteração de cardápio
        # entende-se que ele responde pela DRE em que a escola está contida
        return True
