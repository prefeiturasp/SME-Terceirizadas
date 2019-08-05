from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from xworkflows import InvalidTransitionError

from .permissions import (
    SolicitacaoUnificadaPermission, PodeIniciarSolicitacaoUnificadaPermission,
    PodeIniciarSolicitacaoKitLancheAvulsaPermission)
from .serializers import serializers
from .serializers import serializers_create
from .. import models


class MotivoSolicitacaoUnificadaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.MotivoSolicitacaoUnificada.objects.all()
    serializer_class = serializers.MotivoSolicitacaoUnificadaSerializer


class KitLancheViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = models.KitLanche.objects.all()
    serializer_class = serializers.KitLancheSerializer


class SolicitacaoKitLancheAvulsaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.SolicitacaoKitLancheAvulsa.objects.all()
    serializer_class = serializers.SolicitacaoKitLancheAvulsaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.SolicitacaoKitLancheAvulsaCreationSerializer
        return serializers.SolicitacaoKitLancheAvulsaSerializer

    # TODO: com as permissoes feitas, somente uma pessoa com permissao dentro da escola poder pedir
    # usar PermissionClasses...
    @action(detail=False, url_path="minhas-solicitacoes")
    def minhas_solicitacoes(self, request):
        usuario = request.user
        solicitacoes_unificadas = models.SolicitacaoKitLancheAvulsa.objects.filter(
            criado_por=usuario,
            status=models.SolicitacaoKitLancheAvulsa.workflow_class.RASCUNHO
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission])
    def inicio_de_pedido(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.inicia_fluxo(user=request.user)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    def destroy(self, request, *args, **kwargs):
        solicitacao_kit_lanche_avulsa = self.get_object()
        if solicitacao_kit_lanche_avulsa.pode_excluir:
            return super().destroy(request, *args, **kwargs)


class SolicitacaoKitLancheUnificadaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.SolicitacaoKitLancheUnificada.objects.all()
    serializer_class = serializers.SolicitacaoKitLancheUnificadaSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    # TODO: permitir atualizar (update) os EscolaQuantidade alinhados.
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.SolicitacaoKitLancheUnificadaCreationSerializer
        return serializers.SolicitacaoKitLancheUnificadaSerializer

    @action(detail=False)
    def minhas_solicitacoes(self, request):
        usuario = request.user
        solicitacoes_unificadas = models.SolicitacaoKitLancheUnificada.objects.filter(
            criado_por=usuario,
            status=models.SolicitacaoKitLancheUnificada.workflow_class.RASCUNHO
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = serializers.SolicitacaoKitLancheUnificadaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path="inicio-pedido", permission_classes=[PodeIniciarSolicitacaoUnificadaPermission])
    def inicio_de_pedido(self, request, uuid=None):
        solicitacao_unificada = self.get_object()
        try:
            solicitacao_unificada.inicia_fluxo(user=request.user)
            serializer = self.get_serializer(solicitacao_unificada)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)


class EscolaQuantidadeViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.EscolaQuantidade.objects.all()
    serializer_class = serializers.EscolaQuantidadeSerializer
    permission_classes = [SolicitacaoUnificadaPermission]

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.EscolaQuantidadeCreationSerializer
        return serializers.EscolaQuantidadeSerializer
