from rest_framework import permissions


class PodeIniciarAlteracaoCardapioPermission(permissions.BasePermission):
    message = 'Você não tem permissão para iniciar um pedido de alteração de cardápio.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de iniciar o pedido de alteração de cardápio
        # entende-se que ele responde pela escola
        return True


class PodeAprovarPelaDREAlteracaoCardapioPermission(permissions.BasePermission):
    message = 'Você não tem permissão para aprovar, pela DRE, um pedido de alteração de cardápio.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de
        # aprovar da escola o pedido de alteração de cardápio
        # entende-se que ele responde pela DRE em que a escola está contida
        return True


class PodePedirRevisaoPelaDREAlteracaoCardapioPermission(permissions.BasePermission):
    message = 'Você não tem permissão para pedir revisão, pela DRE, de um pedido de alteração de cardápio.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de
        # aprovar da escola o pedido de alteração de cardápio
        # entende-se que ele responde pela DRE em que a escola está contida
        return True


class PodeIniciarInversaoDeDiaDeCardapioPermission(permissions.BasePermission):
    message = 'Você não tem permissão para aprovar um pedido de inversão de dia de cardápio.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de iniciar o pedido de inversão de dia de cardápio
        # aprovar da escola o pedido de inversão de dia de cardápio
        # entende-se que ele responde pela DRE em que a escola está contida
        return True


class PodeIniciarSuspensaoDeAlimentacaoPermission(permissions.BasePermission):
    message = 'Você não tem permissão para enviar um pedido de suspensão de alimentação.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de iniciar o pedido de inversão de dia de cardápio
        # aprovar da escola o pedido de inversão de dia de cardápio
        # entende-se que ele responde pela DRE em que a escola está contida
        return True


class PodeTomarCienciaSuspensaoDeAlimentacaoPermission(permissions.BasePermission):
    message = 'Você não tem permissão para tomar ciencia de suspensão de alimentação.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de tomar ciencia de suspensao de alimentação
        # aprovar da escola o pedido de inversão de dia de cardápio
        # entende-se que ele responde pela DRE em que a escola está contida
        return True


class PodeAprovarPelaCODAEAlteracaoCardapioPermission(permissions.BasePermission):
    message = 'Você não tem permissão para aprovar, pela CODAE, um pedido de alteração de cardápio.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de
        # aprovar da escola o pedido de alteração de cardápio
        # entende-se que ele responde pela DRE em que a escola está contida
        return True


class PodeRecusarPelaCODAEAlteracaoCardapioPermission(permissions.BasePermission):
    message = 'Você não tem permissão para reprovar, pela CODAE, um pedido de alteração de cardápio.'

    def has_object_permission(self, request, view, alimentacao_continua):
        # TODO: verificar se esse user (request.user) tem permissão de
        # aprovar da escola o pedido de alteração de cardápio
        # entende-se que ele responde pela DRE em que a escola está contida
        return True
