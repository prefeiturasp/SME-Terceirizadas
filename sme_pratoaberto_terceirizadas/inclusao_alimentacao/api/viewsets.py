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
        solicitacoes_unificadas = models.GrupoInclusaoAlimentacaoNormal.objects.filter(
            criado_por=usuario,
            status=models.GrupoInclusaoAlimentacaoNormal.workflow_class.RASCUNHO
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = serializers.GrupoInclusaoAlimentacaoNormalSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[PodeIniciarInclusaoAlimentacaoContinuaPermission])
    def inicio_de_pedido(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.inicia_fluxo(user=request.user, notificar=True)
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

    @action(detail=False, url_path="pedidos-prioritarios")
    def pedidos_prioritarios(self, request):
        usuario = request.user
        solicitacoes_unificadas = models.InclusaoAlimentacaoContinua.objects.filter(
            criado_por=usuario,
            status__in=usuario.status_possiveis,
            data_inicial__lte=obter_dias_uteis_apos_hoje(2)
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = serializers.InclusaoAlimentacaoContinuaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="pedidos-no-limite")
    def pedidos_no_limite(self, request):
        usuario = request.user
        solicitacoes_unificadas = models.InclusaoAlimentacaoContinua.objects.filter(
            criado_por=usuario,
            status=models.InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR,
            data_inicial__gt=obter_dias_uteis_apos_hoje(2),
            data_inicial__lt=obter_dias_uteis_apos_hoje(5)
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = serializers.InclusaoAlimentacaoContinuaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="pedidos-no-prazo")
    def pedidos_no_prazo(self, request):
        usuario = request.user
        solicitacoes_unificadas = models.InclusaoAlimentacaoContinua.objects.filter(
            criado_por=usuario,
            status=models.InclusaoAlimentacaoContinua.workflow_class.DRE_A_VALIDAR,
            data_inicial__gte=obter_dias_uteis_apos_hoje(5),
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = serializers.InclusaoAlimentacaoContinuaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[PodeIniciarInclusaoAlimentacaoContinuaPermission])
    def inicio_de_pedido(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        try:
            alimentacao_continua.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission])
    def confirma_pedido(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        try:
            alimentacao_continua.dre_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission])
    def codae_aprovou(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        try:
            alimentacao_continua.codae_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission])
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
