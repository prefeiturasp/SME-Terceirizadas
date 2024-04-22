from rest_framework.permissions import BasePermission

from sme_terceirizadas.dados_comuns.constants import DILOG_QUALIDADE


class PermissaoParaVisualizarQuestoesConferencia(BasePermission):
    PERFIS_PERMITIDOS = [DILOG_QUALIDADE]

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous
            and usuario.vinculo_atual
            and usuario.vinculo_atual.perfil.nome in self.PERFIS_PERMITIDOS
        )


class PermissaoParaCadastrarFichaRecebimento(BasePermission):
    PERFIS_PERMITIDOS = [DILOG_QUALIDADE]

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous
            and usuario.vinculo_atual
            and usuario.vinculo_atual.perfil.nome in self.PERFIS_PERMITIDOS
        )
