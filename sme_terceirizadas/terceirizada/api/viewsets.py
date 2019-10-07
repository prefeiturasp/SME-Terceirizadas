from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers.serializers import (
    EditalContratosSerializer, EditalSerializer
)
from ...dados_comuns.constants import FILTRO_PADRAO_PEDIDOS, SEM_FILTRO
from ...escola.api.serializers import TerceirizadaSerializer
from .serializers.serializers_create import EditalContratosCreateSerializer, TerceirizadaCreateSerializer
from ..models import Edital, Terceirizada
from ...paineis_consolidados.api.serializers import (
    SolicitacoesSerializer
)


class EditalViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalSerializer
    queryset = Edital.objects.all()


class TerceirizadaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = TerceirizadaSerializer
    queryset = Terceirizada.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TerceirizadaCreateSerializer
        return TerceirizadaSerializer

    @action(detail=True,
            url_path=f'solicitacoes-pendentes-para-mim/{FILTRO_PADRAO_PEDIDOS}')
    def solicitacoes_pendentes_para_mim(self, request, uuid=None, filtro_aplicado=SEM_FILTRO):
        terceirizada = self.get_object()
        pendentes = terceirizada.solicitacoes_pendentes(filtro_aplicado=filtro_aplicado)
        page = self.paginate_queryset(pendentes)
        serializer = SolicitacoesSerializer(
            page, many=True
        )
        return self.get_paginated_response(serializer.data)

class EditalContratosViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalContratosSerializer
    queryset = Edital.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EditalContratosCreateSerializer
        return EditalContratosSerializer
