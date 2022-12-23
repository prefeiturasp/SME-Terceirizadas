from rest_framework.permissions import BasePermission

from ..escola.models import Codae, DiretoriaRegional, Escola
from ..terceirizada.models import Terceirizada
from .constants import (
    ADMINISTRADOR_CODAE_DILOG_CONTABIL,
    ADMINISTRADOR_CODAE_DILOG_JURIDICO,
    ADMINISTRADOR_CODAE_GABINETE,
    ADMINISTRADOR_DIETA_ESPECIAL,
    ADMINISTRADOR_DISTRIBUIDORA,
    ADMINISTRADOR_ESCOLA_ABASTECIMENTO,
    ADMINISTRADOR_FORNECEDOR,
    ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    ADMINISTRADOR_GESTAO_PRODUTO,
    ADMINISTRADOR_MEDICAO,
    ADMINISTRADOR_SUPERVISAO_NUTRICAO,
    ADMINISTRADOR_UE_DIRETA,
    ADMINISTRADOR_UE_MISTA,
    ADMINISTRADOR_UE_PARCEIRA,
    COORDENADOR_CODAE_DILOG_LOGISTICA,
    COORDENADOR_DIETA_ESPECIAL,
    COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    COORDENADOR_GESTAO_PRODUTO,
    COORDENADOR_LOGISTICA,
    COORDENADOR_SUPERVISAO_NUTRICAO,
    COORDENADOR_SUPERVISAO_NUTRICAO_MANIFESTACAO,
    DILOG_CRONOGRAMA,
    DILOG_DIRETORIA,
    DILOG_QUALIDADE,
    DINUTRE_DIRETORIA
)


def usuario_eh_nutricodae(user):
    return user.vinculo_atual.perfil.nome in [COORDENADOR_DIETA_ESPECIAL,
                                              ADMINISTRADOR_DIETA_ESPECIAL]


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
        if hasattr(obj, 'escola') and hasattr(obj, 'rastro_escola'):
            return usuario.vinculo_atual.instituicao in [obj.escola, obj.rastro_escola]
        elif hasattr(obj, 'escola'):
            return usuario.vinculo_atual.instituicao == obj.escola
        elif hasattr(obj, 'rastro_escola'):
            return usuario.vinculo_atual.instituicao == obj.rastro_escola
        else:
            return False


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
                                                  ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                  ADMINISTRADOR_MEDICAO]
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
                                                  COORDENADOR_SUPERVISAO_NUTRICAO,
                                                  ADMINISTRADOR_SUPERVISAO_NUTRICAO,
                                                  COORDENADOR_SUPERVISAO_NUTRICAO_MANIFESTACAO,
                                                  ADMINISTRADOR_MEDICAO]
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
                                                      ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                      COORDENADOR_SUPERVISAO_NUTRICAO,
                                                      COORDENADOR_SUPERVISAO_NUTRICAO_MANIFESTACAO,
                                                      ADMINISTRADOR_MEDICAO]
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
                                                      ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                      COORDENADOR_SUPERVISAO_NUTRICAO,
                                                      COORDENADOR_SUPERVISAO_NUTRICAO_MANIFESTACAO,
                                                      ADMINISTRADOR_MEDICAO]
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
                usuario.vinculo_atual.instituicao in [obj.escola, obj.rastro_escola, obj.escola_destino]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, DiretoriaRegional):
            return (
                usuario.vinculo_atual.instituicao in [obj.escola.diretoria_regional, obj.rastro_dre]
            )
        elif isinstance(usuario.vinculo_atual.instituicao, Codae):
            return (
                usuario.vinculo_atual.perfil.nome in [COORDENADOR_DIETA_ESPECIAL,
                                                      ADMINISTRADOR_DIETA_ESPECIAL,
                                                      COORDENADOR_SUPERVISAO_NUTRICAO,
                                                      COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                      ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                                      ADMINISTRADOR_SUPERVISAO_NUTRICAO,
                                                      COORDENADOR_SUPERVISAO_NUTRICAO_MANIFESTACAO,
                                                      ADMINISTRADOR_MEDICAO]
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
                                                          COORDENADOR_SUPERVISAO_NUTRICAO,
                                                          ADMINISTRADOR_SUPERVISAO_NUTRICAO]
                )
            )
        )


class UsuarioDilog(BasePermission):
    """Permite acesso a usuários DILOG com vinculo a CODAE."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Codae) and
            usuario.vinculo_atual.perfil.nome in [COORDENADOR_LOGISTICA, COORDENADOR_CODAE_DILOG_LOGISTICA]
        )


class UsuarioCodaeDilog(BasePermission):
    """Permite acesso a usuários do perfil CODAE DILOG."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Codae) and
            usuario.vinculo_atual.perfil.nome in [COORDENADOR_CODAE_DILOG_LOGISTICA]
        )


class UsuarioDistribuidor(BasePermission):
    """Permite acesso a usuários com vinculo a Distribuidoras."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Terceirizada) and
            usuario.vinculo_atual.perfil.nome in [ADMINISTRADOR_DISTRIBUIDORA]
        )


class UsuarioEscolaAbastecimento(BasePermission):
    """Permite acesso a usuários com vinculo a uma Escola de Abastecimento."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            isinstance(usuario.vinculo_atual.instituicao, Escola) and
            usuario.vinculo_atual.perfil.nome in [
                ADMINISTRADOR_ESCOLA_ABASTECIMENTO, ADMINISTRADOR_UE_DIRETA, ADMINISTRADOR_UE_MISTA,
                ADMINISTRADOR_UE_PARCEIRA
            ]
        )


class UsuarioDilogOuDistribuidor(BasePermission):
    """Permite acesso a usuários com vinculo a dilogCodae e distribuidor."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                isinstance(usuario.vinculo_atual.instituicao, Codae) and
                usuario.vinculo_atual.perfil.nome in [COORDENADOR_LOGISTICA, COORDENADOR_CODAE_DILOG_LOGISTICA] or
                (
                    isinstance(usuario.vinculo_atual.instituicao, Terceirizada) and
                    usuario.vinculo_atual.perfil.nome in [ADMINISTRADOR_DISTRIBUIDORA]
                )
            )
        )


class UsuarioDilogOuDistribuidorOuEscolaAbastecimento(BasePermission):
    """Acesso permitido a usuários vinculados a uma escola abastecimento ou cordenador dilog ou distibuidor."""

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                (
                    isinstance(usuario.vinculo_atual.instituicao, Codae) and
                    usuario.vinculo_atual.perfil.nome in [COORDENADOR_LOGISTICA, COORDENADOR_CODAE_DILOG_LOGISTICA]
                ) or
                (
                    isinstance(usuario.vinculo_atual.instituicao, Terceirizada) and
                    usuario.vinculo_atual.perfil.nome in [ADMINISTRADOR_DISTRIBUIDORA]
                ) or
                (
                    isinstance(usuario.vinculo_atual.instituicao, Escola) and
                    usuario.vinculo_atual.perfil.nome in [
                        ADMINISTRADOR_ESCOLA_ABASTECIMENTO, ADMINISTRADOR_UE_DIRETA, ADMINISTRADOR_UE_MISTA,
                        ADMINISTRADOR_UE_PARCEIRA
                    ]
                )
            )
        )


class PermissaoParaListarEntregas(BasePermission):

    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                (
                    isinstance(usuario.vinculo_atual.instituicao, Codae) and
                    usuario.vinculo_atual.perfil.nome in [
                        COORDENADOR_LOGISTICA, COORDENADOR_CODAE_DILOG_LOGISTICA, COORDENADOR_SUPERVISAO_NUTRICAO,
                        ADMINISTRADOR_CODAE_GABINETE, ADMINISTRADOR_CODAE_DILOG_CONTABIL,
                        ADMINISTRADOR_CODAE_DILOG_JURIDICO
                    ]
                ) or
                (
                    isinstance(usuario.vinculo_atual.instituicao, Terceirizada) and
                    usuario.vinculo_atual.perfil.nome in [ADMINISTRADOR_DISTRIBUIDORA]
                ) or
                (
                    isinstance(usuario.vinculo_atual.instituicao, DiretoriaRegional)
                )
            )
        )


class PermissaoParaVisualizarCronograma(BasePermission):
    # TODO: Conforme solicitado pelos P.Os, usuários Logistica tem acesso temporariamente p/ visualização do cronograma.
    #  Após finalização da definição de permissionamento deve se remover COORDENADOR_CODAE_DILOG_LOGISTICA e
    #  COORDENADOR_LOGISTICA deste permissionamento.
    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                (
                    isinstance(usuario.vinculo_atual.instituicao, Codae) or
                    isinstance(usuario.vinculo_atual.instituicao, Terceirizada) and
                    usuario.vinculo_atual.perfil.nome in [DILOG_CRONOGRAMA, DILOG_QUALIDADE, DILOG_DIRETORIA,
                                                          DINUTRE_DIRETORIA, COORDENADOR_CODAE_DILOG_LOGISTICA,
                                                          COORDENADOR_LOGISTICA, ADMINISTRADOR_FORNECEDOR]
                )
            )
        )


class PermissaoParaCriarCronograma(BasePermission):
    # TODO: Conforme solicitado pelos P.Os, usuários Logistica tem acesso temporariamente ao Cadastro de Cronograma.
    #  Após finalização da definição de permissionamento deve se remover COORDENADOR_CODAE_DILOG_LOGISTICA e
    #  COORDENADOR_LOGISTICA deste permissionamento.
    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                (
                    isinstance(usuario.vinculo_atual.instituicao, Codae) and
                    usuario.vinculo_atual.perfil.nome in [DILOG_CRONOGRAMA, COORDENADOR_CODAE_DILOG_LOGISTICA,
                                                          COORDENADOR_LOGISTICA]
                )
            )
        )


class PermissaoParaConfirmarCronograma(BasePermission):
    # Apenas empresas do tipo fornecedor com perfil ADMINISTRADOR_FORNECEDOR podem confirmar
    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                (
                    isinstance(usuario.vinculo_atual.instituicao, Terceirizada) and
                    usuario.vinculo_atual.perfil.nome == ADMINISTRADOR_FORNECEDOR
                )
            )
        )


class PermissaoParaCadastrarLaboratorio(BasePermission):
    # Apenas DILOG_QUALIDADE tem acesso a tela de cadastro de Laboratórios.
    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                (
                    isinstance(usuario.vinculo_atual.instituicao, Codae) and
                    usuario.vinculo_atual.perfil.nome in [DILOG_QUALIDADE]
                )
            )
        )


class PermissaoParaCadastrarVisualizarEmbalagem(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        return (
            not usuario.is_anonymous and
            usuario.vinculo_atual and
            (
                (
                    isinstance(usuario.vinculo_atual.instituicao, Codae) and
                    usuario.vinculo_atual.perfil.nome in [DILOG_QUALIDADE, DILOG_CRONOGRAMA]
                )
            )
        )


class ViewSetActionPermissionMixin:
    def get_permissions(self):
        """Return the permission classes based on action.

        Look for permission classes in a dict mapping action to
        permission classes array, ie.:

        class MyViewSet(ViewSetActionPermissionMixin, ViewSet):
            ...
            permission_classes = [AllowAny]
            permission_action_classes = {
                'list': [IsAuthenticated]
                'create': [IsAdminUser]
                'my_action': [MyCustomPermission]
            }

            @action(...)
            def my_action:
                ...

        If there is no action in the dict mapping, then the default
        permission_classes is returned. If a custom action has its
        permission_classes defined in the action decorator, then that
        supercedes the value defined in the dict mapping.
        """
        try:
            return [
                permission()
                for permission in self.permission_action_classes[self.action]
            ]
        except KeyError:
            if self.action:
                action_func = getattr(self, self.action, {})
                action_func_kwargs = getattr(action_func, 'kwargs', {})
                permission_classes = action_func_kwargs.get(
                    'permission_classes'
                )
            else:
                permission_classes = None

            return [
                permission()
                for permission in (
                    permission_classes or self.permission_classes
                )
            ]
