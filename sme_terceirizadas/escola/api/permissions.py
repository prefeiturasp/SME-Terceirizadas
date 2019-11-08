from rest_framework import permissions

from ...dados_comuns.constants import COGESTOR, DIRETOR, SUPLENTE


class PodeCriarAdministradoresDaEscola(permissions.BasePermission):
    message = 'O seu perfil não tem permissao para criar administradores da escola'

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario.is_anonymous:
            perfil_diretor = usuario.vinculo_atual.perfil.nome == DIRETOR
            return perfil_diretor
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        tem_vinculo_que_pode_criar_administradores = user.vinculo_atual.instituicao == obj
        if tem_vinculo_que_pode_criar_administradores:
            return True
        return False


class PodeCriarAdministradoresDaDiretoriaRegional(permissions.BasePermission):
    message = 'O seu perfil não tem permissao para criar administradores da diretoria regional'

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario.is_anonymous:
            perfil_cogestor_ou_suplente = usuario.vinculo_atual.perfil.nome in [COGESTOR, SUPLENTE]
            return perfil_cogestor_ou_suplente
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        tem_vinculo_que_pode_criar_administradores = user.vinculo_atual.instituicao == obj
        if tem_vinculo_que_pode_criar_administradores:
            return True
        return False
