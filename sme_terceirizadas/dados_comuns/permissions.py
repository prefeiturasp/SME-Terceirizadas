from rest_framework.permissions import BasePermission

from ..escola.models import Codae, DiretoriaRegional, Escola
from ..terceirizada.models import Terceirizada
from .constants import (
    ADMINISTRADOR_DIETA_ESPECIAL,
    ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    ADMINISTRADOR_GESTAO_PRODUTO,
    COORDENADOR_DIETA_ESPECIAL,
    COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    COORDENADOR_GESTAO_PRODUTO,
    SUPERVISAO_NUTRICAO
)


def usuario_eh_nutricodae(user):
    return user.vinculo_atual.perfil.nome in [COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                              ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA]


class UsuarioEscola(BasePermission):
    """Permite acesso a usuários com vinculo a uma Escola."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Escola)
        )

    """Permite acesso ao objeto se o objeto pertence a essa escola."""

    def has_object_permission(self, request, view, obj):
        usuario = request.user
        return (
            usuario.vinculo_atual.instituicao in [obj.escola, obj.rastro_escola]
        )


class UsuarioDiretoriaRegional(BasePermission):
    """Permite acesso a usuários com vinculo a uma Diretoria Regional."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, DiretoriaRegional)
        )

    """Permite acesso ao objeto se o objeto pertence a essa Diretoria Regional."""

    def has_object_permission(self, request, view, obj):
        usuario = request.user
        # TODO: ver uma melhor forma de organizar esse try-except
        try:  # solicitacoes normais
            retorno = usuario.vinculo_atual.instituicao in [obj.escola.diretoria_regional, obj.rastro_dre]
        except AttributeError:  # solicitacao unificada
            retorno = usuario.vinculo_atual.instituicao in [obj.rastro_dre, obj.diretoria_regional]
        return retorno


class UsuarioCODAEGestaoAlimentacao(BasePermission):
    """Permite acesso a usuários com vinculo a CODAE - Gestão de Alimentação."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Codae) and
            usuario.vinculo_atual.perfil.nome in [COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                  ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA]
        )


class UsuarioCODAEDietaEspecial(BasePermission):
    """Permite acesso a usuários com vinculo a CODAE - Dieta Especial."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Codae) and
            usuario.vinculo_atual.perfil.nome in [COORDENADOR_DIETA_ESPECIAL,
                                                  ADMINISTRADOR_DIETA_ESPECIAL]
        )


class UsuarioNutricionista(BasePermission):
    """Permite acesso a usuários com vinculo a CODAE - Dieta Especial."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Codae) and
            usuario.vinculo_atual.perfil.nome in [COORDENADOR_DIETA_ESPECIAL,
                                                  ADMINISTRADOR_DIETA_ESPECIAL,
                                                  SUPERVISAO_NUTRICAO]
        )


class UsuarioCODAEGestaoProduto(BasePermission):
    """Permite acesso a usuários com vinculo a CODAE - Gestão de Produto."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Codae) and
            usuario.vinculo_atual.perfil.nome in [COORDENADOR_GESTAO_PRODUTO,
                                                  ADMINISTRADOR_GESTAO_PRODUTO]
        )


class UsuarioTerceirizada(BasePermission):
    """Permite acesso a usuários com vinculo a uma Terceirizada."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Terceirizada)
        )

    """Permite acesso ao objeto se o objeto pertence a essa Diretoria Regional"""

    def has_object_permission(self, request, view, obj):
        usuario = request.user
        # TODO: ver uma melhor forma de organizar esse try-except
        try:  # solicitacoes normais
            retorno = usuario.vinculo_atual.instituicao in [obj.escola.lote.terceirizada, obj.rastro_terceirizada]
        except AttributeError:  # solicitacao unificada
            retorno = usuario.vinculo_atual.instituicao == obj.rastro_terceirizada
        return retorno


class PermissaoParaRecuperarObjeto(BasePermission):
    """Permite acesso ao objeto se o objeto pertence ao usuário."""

    def has_object_permission(self, request, view, obj):  # noqa
        usuario = request.user
        if isinstance(usuario.vinculo_atual.instituicao, Escola):
            return (
                usuario.vinculo_atual.instituicao in [obj.escola, obj.rastro_escola]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, DiretoriaRegional):
            return (
                usuario.vinculo_atual.instituicao in [obj.escola.diretoria_regional, obj.rastro_dre]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, Codae):
            return (
                usuario.vinculo_atual.perfil.nome in [COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                      ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, Terceirizada):
            try:  # solicitacoes normais
                retorno = usuario.vinculo_atual.instituicao in [obj.escola.lote.terceirizada, obj.rastro_terceirizada]
            except AttributeError:  # solicitacao unificada
                retorno = usuario.vinculo_atual.instituicao == obj.rastro_terceirizada
            return retorno


class PermissaoParaRecuperarSolicitacaoUnificada(BasePermission):
    """Permite acesso ao objeto se a solicitação unificada pertence ao usuário."""

    def has_object_permission(self, request, view, obj):  # noqa
        usuario = request.user
        if isinstance(usuario.vinculo_atual.instituicao, Escola):
            return (
                obj.possui_escola_na_solicitacao(usuario.vinculo_atual.instituicao) or
                usuario.vinculo_atual.instituicao in obj.rastro_escolas.all()
            )
        elif isinstance(usuario.vinculo_atual.instituicao, DiretoriaRegional):
            return (
                usuario.vinculo_atual.instituicao in [obj.diretoria_regional, obj.rastro_dre]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, Codae):
            return (
                usuario.vinculo_atual.perfil.nome in [COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                      ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, Terceirizada):
            return (
                usuario.vinculo_atual.instituicao in [obj.lote, obj.rastro_terceirizada]
            )


class PermissaoParaRecuperarDietaEspecial(BasePermission):
    """Permite acesso ao objeto se a dieta especial pertence ao usuário."""

    def has_object_permission(self, request, view, obj):  # noqa
        usuario = request.user
        if isinstance(usuario.vinculo_atual.instituicao, Escola):
            return (
                usuario.vinculo_atual.instituicao in [obj.escola, obj.rastro_escola]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, DiretoriaRegional):
            return (
                usuario.vinculo_atual.instituicao in [obj.escola.diretoria_regional, obj.rastro_dre]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, Codae):
            return (
                usuario.vinculo_atual.perfil.nome in [COORDENADOR_DIETA_ESPECIAL,
                                                      ADMINISTRADOR_DIETA_ESPECIAL,
                                                      SUPERVISAO_NUTRICAO]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, Terceirizada):
            return (
                usuario.vinculo_atual.instituicao in [obj.escola.lote.terceirizada, obj.rastro_terceirizada]
            )


class PermissaoParaReclamarDeProduto(BasePermission):
    """Permite acesso a usuários com vinculo a uma Escola ou Nutricionistas CODAE."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                isinstance(usuario.vinculo_atual.instituicao, Escola) or
                (
                    isinstance(usuario.vinculo_atual.instituicao, Codae) and
                    usuario.vinculo_atual.perfil.nome in [COORDENADOR_DIETA_ESPECIAL,
                                                          ADMINISTRADOR_DIETA_ESPECIAL,
                                                          SUPERVISAO_NUTRICAO]
                )
            )
        )
