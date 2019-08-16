from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from xworkflows import InvalidTransitionError

from sme_pratoaberto_terceirizadas.dados_comuns.utils import obter_dias_uteis_apos_hoje
from .permissions import (
    PodeIniciarInclusaoAlimentacaoContinuaPermission,
    PodeAprovarAlimentacaoContinuaDaEscolaPermission
)
from .serializers import serializers, serializers_create
from .. import models


class MotivoInclusaoContinuaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = models.MotivoInclusaoContinua.objects.all()
    serializer_class = serializers.MotivoInclusaoContinuaSerializer


class MotivoInclusaoNormalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = models.MotivoInclusaoNormal.objects.all()
    serializer_class = serializers.MotivoInclusaoNormalSerializer


class InclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.InclusaoAlimentacaoNormal.objects.all()
    serializer_class = serializers.InclusaoAlimentacaoNormalSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.InclusaoAlimentacaoNormalCreationSerializer
        return serializers.InclusaoAlimentacaoNormalSerializer


class GrupoInclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.GrupoInclusaoAlimentacaoNormal.objects.all()
    serializer_class = serializers.GrupoInclusaoAlimentacaoNormalSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.GrupoInclusaoAlimentacaoNormalCreationSerializer
        return serializers.GrupoInclusaoAlimentacaoNormalSerializer

    @action(detail=False, url_path="minhas-solicitacoes")
    def minhas_solicitacoes(self, request):
        usuario = request.user
        alimentacao_normal = models.GrupoInclusaoAlimentacaoNormal.objects.filter(
            criado_por=usuario,
            status=models.GrupoInclusaoAlimentacaoNormal.workflow_class.RASCUNHO
        )
        page = self.paginate_queryset(alimentacao_normal)
        serializer = serializers.GrupoInclusaoAlimentacaoNormalSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="pedidos-prioritarios-diretoria-regional")
    def pedidos_prioritarios_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_normais = diretoria_regional.inclusoes_normais_das_minhas_escolas_no_prazo_vencendo
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="pedidos-no-limite-diretoria-regional")
    def pedidos_no_limite_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_normais = diretoria_regional.inclusoes_normais_das_minhas_escolas_no_prazo_limite
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="pedidos-no-prazo-diretoria-regional")
    def pedidos_no_prazo_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_normais = diretoria_regional.inclusoes_normais_das_minhas_escolas_no_prazo_regular
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[PodeIniciarInclusaoAlimentacaoContinuaPermission], methods=['patch'])
    def inicio_de_pedido(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission], methods=['patch'])
    def confirma_pedido(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.dre_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    def destroy(self, request, *args, **kwargs):
        alimentacao_normal = self.get_object()
        if alimentacao_normal.pode_excluir:
            return super().destroy(request, *args, **kwargs)


class InclusaoAlimentacaoContinuaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.InclusaoAlimentacaoContinua.objects.all()
    serializer_class = serializers.InclusaoAlimentacaoContinuaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.InclusaoAlimentacaoContinuaCreationSerializer
        return serializers.InclusaoAlimentacaoContinuaSerializer

    @action(detail=False, url_path="minhas-solicitacoes")
    def minhas_solicitacoes(self, request):
        usuario = request.user
        solicitacoes_unificadas = models.InclusaoAlimentacaoContinua.objects.filter(
            criado_por=usuario,
            status=models.InclusaoAlimentacaoContinua.workflow_class.RASCUNHO
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = serializers.InclusaoAlimentacaoContinuaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path="pedidos-prioritarios-diretoria-regional/"
                     "(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)")
    def pedidos_prioritarios_diretoria_regional(self, request, filtro_aplicado="sem_filtro"):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path="pedidos-no-limite-diretoria-regional/"
                     "(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)")
    def pedidos_no_limite_diretoria_regional(self, request, filtro_aplicado="sem_filtro"):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path="pedidos-no-prazo-diretoria-regional/"
                     "(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)")
    def pedidos_no_prazo_diretoria_regional(self, request, filtro_aplicado="sem_filtro"):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[PodeIniciarInclusaoAlimentacaoContinuaPermission], methods=['patch'])
    def inicio_de_pedido(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        try:
            alimentacao_continua.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission], methods=['patch'])
    def confirma_pedido(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        try:
            alimentacao_continua.dre_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission], methods=['patch'])
    def codae_aprovou(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        try:
            alimentacao_continua.codae_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission], methods=['patch'])
    def terceirizada_tomou_ciencia(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        try:
            alimentacao_continua.terceirizada_tomou_ciencia(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    def destroy(self, request, *args, **kwargs):
        alimentacao_continua = self.get_object()
        if alimentacao_continua.pode_excluir:
            return super().destroy(request, *args, **kwargs)
