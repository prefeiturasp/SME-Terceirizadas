from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from xworkflows import InvalidTransitionError

from ...dados_comuns import constants
from ...dados_comuns.permissions import (
    PermissaoParaRecuperarObjeto,
    UsuarioCODAEGestaoAlimentacao,
    UsuarioDiretoriaRegional,
    UsuarioEscola,
    UsuarioTerceirizada
)
from ...relatorios.relatorios import relatorio_inclusao_alimentacao_continua, relatorio_inclusao_alimentacao_normal
from ..models import (
    GrupoInclusaoAlimentacaoNormal,
    InclusaoAlimentacaoContinua,
    InclusaoAlimentacaoDaCEI,
    MotivoInclusaoContinua,
    MotivoInclusaoNormal
)
from .serializers import serializers, serializers_create


class InclusaoAlimentacaoDaCEIViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = InclusaoAlimentacaoDaCEI.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.InclusaoAlimentacaoDaCEISerializer

    def get_permissions(self):
        if self.action in ['list', 'update']:
            self.permission_classes = (IsAdminUser,)
        elif self.action == 'retrieve':
            self.permission_classes = (IsAuthenticated, PermissaoParaRecuperarObjeto)
        elif self.action in ['create', 'destroy']:
            self.permission_classes = (UsuarioEscola,)
        return super(InclusaoAlimentacaoDaCEIViewSet, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.InclusaoAlimentacaoDaCEICreateSerializer
        return serializers.InclusaoAlimentacaoDaCEISerializer

    @action(detail=False, url_path=constants.SOLICITACOES_DO_USUARIO, permission_classes=(UsuarioEscola,))
    def minhas_solicitacoes(self, request):
        usuario = request.user
        alimentacoes_normais = InclusaoAlimentacaoDaCEI.get_solicitacoes_rascunho(usuario)
        page = self.paginate_queryset(alimentacoes_normais)
        serializer = serializers.InclusaoAlimentacaoDaCEISerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    #
    # IMPLEMENTACAO DO FLUXO
    #

    @action(detail=True,
            methods=['patch'],
            url_path=constants.ESCOLA_INICIO_PEDIDO)
    def inicio_de_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.inicia_fluxo(user=request.user, )
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)


class MotivoInclusaoContinuaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoInclusaoContinua.objects.all()
    serializer_class = serializers.MotivoInclusaoContinuaSerializer


class MotivoInclusaoNormalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoInclusaoNormal.objects.all()
    serializer_class = serializers.MotivoInclusaoNormalSerializer


class GrupoInclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = GrupoInclusaoAlimentacaoNormal.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.GrupoInclusaoAlimentacaoNormalSerializer

    def get_permissions(self):
        if self.action in ['list', 'update']:
            self.permission_classes = (IsAdminUser,)
        elif self.action == 'retrieve':
            self.permission_classes = (IsAuthenticated, PermissaoParaRecuperarObjeto)
        elif self.action in ['create', 'destroy']:
            self.permission_classes = (UsuarioEscola,)
        return super(GrupoInclusaoAlimentacaoNormalViewSet, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.GrupoInclusaoAlimentacaoNormalCreationSerializer
        return serializers.GrupoInclusaoAlimentacaoNormalSerializer

    @action(detail=False, url_path=constants.SOLICITACOES_DO_USUARIO, permission_classes=(UsuarioEscola,))
    def minhas_solicitacoes(self, request):
        usuario = request.user
        alimentacoes_normais = GrupoInclusaoAlimentacaoNormal.get_solicitacoes_rascunho(usuario)
        page = self.paginate_queryset(alimentacoes_normais)
        serializer = serializers.GrupoInclusaoAlimentacaoNormalSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_CODAE}/{constants.FILTRO_PADRAO_PEDIDOS}',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def solicitacoes_codae(self, request, filtro_aplicado=constants.SEM_FILTRO):
        # TODO: colocar regras de codae CODAE aqui...
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        inclusoes_continuas = codae.grupos_inclusoes_alimentacao_normal_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_TERCEIRIZADA}/{constants.FILTRO_PADRAO_PEDIDOS}',
            permission_classes=(UsuarioTerceirizada,))
    def solicitacoes_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        # TODO: colocar regras de terceirizada aqui...
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        inclusoes_continuas = terceirizada.grupos_inclusoes_alimentacao_normal_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # TODO rever os demais endpoints. Essa action consolida em uma única pesquisa as pesquisas por prioridade.
    @action(detail=False,
            url_path=f'{constants.PEDIDOS_DRE}/{constants.FILTRO_PADRAO_PEDIDOS}',
            permission_classes=(UsuarioDiretoriaRegional,))
    def solicitacoes_diretoria_regional(self, request, filtro_aplicado=constants.SEM_FILTRO):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        inclusoes_alimentacao_normal = diretoria_regional.grupos_inclusoes_alimentacao_normal_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_alimentacao_normal)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-autorizados-diretoria-regional',
            permission_classes=(UsuarioDiretoriaRegional,))
    def solicitacoes_autorizados_diretoria_regional(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        inclusoes_normais = diretoria_regional.inclusoes_normais_autorizadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-reprovados-diretoria-regional',
            permission_classes=(UsuarioDiretoriaRegional,))
    def solicitacoes_reprovados_diretoria_regional(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        inclusoes_normais = diretoria_regional.inclusoes_normais_reprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-autorizados-codae',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def solicitacoes_autorizadas_codae(self, request):
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        inclusoes_normais = codae.inclusoes_normais_autorizadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-reprovados-codae',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def solicitacoes_reprovados_codae(self, request):
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        inclusoes_normais = codae.inclusoes_normais_reprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-autorizados-terceirizada',
            permission_classes=(UsuarioTerceirizada,))
    def solicitacoes_autorizadas_terceirizada(self, request):
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        inclusoes_normais = terceirizada.inclusoes_normais_autorizadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-reprovados-terceirizada',
            permission_classes=(UsuarioTerceirizada,))
    def solicitacoes_reprovados_terceirizada(self, request):
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        inclusoes_normais = terceirizada.inclusoes_normais_reprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['GET'],
            url_path=f'{constants.RELATORIO}',
            permission_classes=[AllowAny])
    def relatorio(self, request, uuid=None):
        return relatorio_inclusao_alimentacao_normal(request, solicitacao=self.get_object())

    #
    # IMPLEMENTACAO DO FLUXO
    #

    @action(detail=True,
            permission_classes=(UsuarioEscola,),
            methods=['patch'],
            url_path=constants.ESCOLA_INICIO_PEDIDO)
    def inicio_de_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.inicia_fluxo(user=request.user, )
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioDiretoriaRegional,),
            methods=['patch'],
            url_path=constants.DRE_VALIDA_PEDIDO)
    def diretoria_regional_valida(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.dre_valida(user=request.user, )
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioDiretoriaRegional,),
            methods=['patch'],
            url_path=constants.DRE_NAO_VALIDA_PEDIDO)
    def diretoria_nao_valida_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.dre_nao_valida(user=request.user, )
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,),
            methods=['patch'],
            url_path=constants.CODAE_AUTORIZA_PEDIDO)
    def codae_autoriza_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            if grupo_alimentacao_normal.status == grupo_alimentacao_normal.workflow_class.DRE_VALIDADO:
                grupo_alimentacao_normal.codae_autoriza(user=request.user)
            else:
                grupo_alimentacao_normal.codae_autoriza_questionamento(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,),
            methods=['patch'],
            url_path=constants.CODAE_QUESTIONA_PEDIDO)
    def codae_questiona_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        observacao_questionamento_codae = request.data.get('observacao_questionamento_codae', '')
        try:
            grupo_alimentacao_normal.codae_questiona(
                user=request.user,
                justificativa=observacao_questionamento_codae
            )
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,),
            methods=['patch'],
            url_path=constants.CODAE_NEGA_PEDIDO)
    def codae_nega_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            if grupo_alimentacao_normal.status == grupo_alimentacao_normal.workflow_class.DRE_VALIDADO:
                grupo_alimentacao_normal.codae_nega(user=request.user)
            else:
                grupo_alimentacao_normal.codae_nega_questionamento(user=request.user)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioTerceirizada,),
            methods=['patch'],
            url_path=constants.TERCEIRIZADA_TOMOU_CIENCIA)
    def terceirizada_toma_ciencia(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.terceirizada_toma_ciencia(user=request.user, )
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioTerceirizada,),
            methods=['patch'],
            url_path=constants.TERCEIRIZADA_RESPONDE_QUESTIONAMENTO)
    def terceirizada_responde_questionamento(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        justificativa = request.data.get('justificativa', '')
        resposta_sim_nao = request.data.get('resposta_sim_nao', False)
        try:
            grupo_alimentacao_normal.terceirizada_responde_questionamento(user=request.user,
                                                                          justificativa=justificativa,
                                                                          resposta_sim_nao=resposta_sim_nao)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioEscola,),
            methods=['patch'],
            url_path=constants.ESCOLA_CANCELA)
    def escola_cancela_pedido(self, request, uuid=None):
        justificativa = request.data.get('justificativa', '')
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.cancelar_pedido(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        inversao_cardapio = self.get_object()
        if inversao_cardapio.pode_excluir:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response(dict(detail='Você só pode excluir quando o status for RASCUNHO.'),
                            status=status.HTTP_403_FORBIDDEN)


class InclusaoAlimentacaoContinuaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = InclusaoAlimentacaoContinua.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.InclusaoAlimentacaoContinuaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.InclusaoAlimentacaoContinuaCreationSerializer
        return serializers.InclusaoAlimentacaoContinuaSerializer

    def get_permissions(self):
        if self.action in ['list', 'update']:
            self.permission_classes = (IsAdminUser,)
        elif self.action == 'retrieve':
            self.permission_classes = (IsAuthenticated, PermissaoParaRecuperarObjeto)
        elif self.action in ['create', 'destroy']:
            self.permission_classes = (UsuarioEscola,)
        return super(InclusaoAlimentacaoContinuaViewSet, self).get_permissions()

    @action(detail=False, url_path=constants.SOLICITACOES_DO_USUARIO, permission_classes=(UsuarioEscola,))
    def minhas_solicitacoes(self, request):
        usuario = request.user
        inclusoes_continuas = InclusaoAlimentacaoContinua.get_solicitacoes_rascunho(usuario)
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_CODAE}/{constants.FILTRO_PADRAO_PEDIDOS}',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def solicitacoes_codae(self, request, filtro_aplicado=constants.SEM_FILTRO):
        # TODO: colocar regras de codae CODAE aqui...
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        inclusoes_continuas = codae.inclusoes_alimentacao_continua_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_TERCEIRIZADA}/{constants.FILTRO_PADRAO_PEDIDOS}',
            permission_classes=(UsuarioTerceirizada,))
    def solicitacoes_terceirizada(self, request, filtro_aplicado=constants.SEM_FILTRO):
        # TODO: colocar regras de terceirizada aqui...
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        inclusoes_continuas = terceirizada.inclusoes_alimentacao_continua_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_DRE}/{constants.FILTRO_PADRAO_PEDIDOS}',
            permission_classes=(UsuarioDiretoriaRegional,))
    def solicitacoes_diretoria_regional(self, request, filtro_aplicado=constants.SEM_FILTRO):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        inclusoes_alimentacao_continua = diretoria_regional.inclusoes_alimentacao_continua_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_alimentacao_continua)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-autorizados-diretoria-regional',
            permission_classes=(UsuarioDiretoriaRegional,))
    def solicitacoes_autorizadas_diretoria_regional(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_autorizadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-reprovados-diretoria-regional',
            permission_classes=(UsuarioDiretoriaRegional,))
    def solicitacoes_reprovados_diretoria_regional(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_reprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-autorizados-codae',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def solicitacoes_autorizadas_codae(self, request):
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        inclusoes_continuas = codae.inclusoes_continuas_autorizadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-reprovados-codae',
            permission_classes=(UsuarioCODAEGestaoAlimentacao,))
    def solicitacoes_reprovados_codae(self, request):
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        inclusoes_continuas = codae.inclusoes_continuas_reprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-autorizados-terceirizada',
            permission_classes=(UsuarioTerceirizada,))
    def solicitacoes_autorizadas_terceirizada(self, request):
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        inclusoes_continuas = terceirizada.inclusoes_continuas_autorizadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-reprovados-terceirizada',
            permission_classes=(UsuarioTerceirizada,))
    def solicitacoes_reprovados_terceirizada(self, request):
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        inclusoes_continuas = terceirizada.inclusoes_continuas_reprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['GET'],
            url_path=f'{constants.RELATORIO}', permission_classes=[AllowAny])
    def relatorio(self, request, uuid=None):
        return relatorio_inclusao_alimentacao_continua(request, solicitacao=self.get_object())

    #
    # IMPLEMENTACAO DO FLUXO
    #

    @action(detail=True,
            permission_classes=(UsuarioEscola,),
            methods=['patch'],
            url_path=constants.ESCOLA_INICIO_PEDIDO)
    def inicio_de_pedido(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        try:
            inclusoes_alimentacao_continua.inicia_fluxo(user=request.user, )
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioDiretoriaRegional,),
            methods=['patch'],
            url_path=constants.DRE_VALIDA_PEDIDO)
    def diretoria_regional_valida(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        try:
            inclusoes_alimentacao_continua.dre_valida(user=request.user, )
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioDiretoriaRegional,),
            methods=['patch'],
            url_path=constants.DRE_NAO_VALIDA_PEDIDO)
    def diretoria_regional_nao_valida_pedido(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        try:
            inclusoes_alimentacao_continua.dre_nao_valida(user=request.user, )
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,),
            methods=['patch'],
            url_path=constants.CODAE_NEGA_PEDIDO)
    def codae_nega_pedido(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        try:
            if inclusoes_alimentacao_continua.status == inclusoes_alimentacao_continua.workflow_class.DRE_VALIDADO:
                inclusoes_alimentacao_continua.codae_nega(user=request.user)
            else:
                inclusoes_alimentacao_continua.codae_nega_questionamento(user=request.user)
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,),
            methods=['patch'],
            url_path=constants.CODAE_AUTORIZA_PEDIDO)
    def codae_autoriza_pedido(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            if inclusoes_alimentacao_continua.status == inclusoes_alimentacao_continua.workflow_class.DRE_VALIDADO:
                inclusoes_alimentacao_continua.codae_autoriza(user=request.user)
            else:
                inclusoes_alimentacao_continua.codae_autoriza_questionamento(user=request.user,
                                                                             justificativa=justificativa)
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoAlimentacao,),
            methods=['patch'],
            url_path=constants.CODAE_QUESTIONA_PEDIDO)
    def codae_questiona_pedido(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        observacao_questionamento_codae = request.data.get('observacao_questionamento_codae', '')
        try:
            inclusoes_alimentacao_continua.codae_questiona(
                user=request.user,
                justificativa=observacao_questionamento_codae
            )
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioTerceirizada,),
            methods=['patch'],
            url_path=constants.TERCEIRIZADA_TOMOU_CIENCIA)
    def terceirizada_toma_ciencia(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        try:
            inclusoes_alimentacao_continua.terceirizada_toma_ciencia(user=request.user, )
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioTerceirizada,),
            methods=['patch'],
            url_path=constants.TERCEIRIZADA_RESPONDE_QUESTIONAMENTO)
    def terceirizada_responde_questionamento(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        justificativa = request.data.get('justificativa', '')
        resposta_sim_nao = request.data.get('resposta_sim_nao', False)
        try:
            inclusoes_alimentacao_continua.terceirizada_responde_questionamento(user=request.user,
                                                                                justificativa=justificativa,
                                                                                resposta_sim_nao=resposta_sim_nao)
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioEscola,),
            methods=['patch'],
            url_path=constants.ESCOLA_CANCELA)
    def escola_cancela_pedido(self, request, uuid=None):
        inclusoes_alimentacao_continua = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            inclusoes_alimentacao_continua.cancelar_pedido(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(inclusoes_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        grupo_alimentacao_normal = self.get_object()
        if grupo_alimentacao_normal.pode_excluir:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response(dict(detail='Você só pode excluir quando o status for RASCUNHO.'),
                            status=status.HTTP_403_FORBIDDEN)
