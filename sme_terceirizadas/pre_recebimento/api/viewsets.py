
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sme_terceirizadas.dados_comuns.permissions import (
    PermissaoParaCriarCronograma,
    PermissaoParaVisualizarCronograma,
    ViewSetActionPermissionMixin
)
from sme_terceirizadas.pre_recebimento.api.filters import CronogramaFilter
from sme_terceirizadas.pre_recebimento.api.paginations import CronogramaPagination
from sme_terceirizadas.pre_recebimento.api.serializers.serializer_create import CronogramaCreateSerializer
from sme_terceirizadas.pre_recebimento.api.serializers.serializers import CronogramaSerializer
from sme_terceirizadas.pre_recebimento.models import Cronograma, EtapasDoCronograma


class CronogramaModelViewSet(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Cronograma.objects.all()
    serializer_class = CronogramaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CronogramaFilter
    pagination_class = CronogramaPagination
    permission_classes = (PermissaoParaVisualizarCronograma,)
    permission_action_classes = {
        'create': [PermissaoParaCriarCronograma],
        'delete': [PermissaoParaCriarCronograma]
    }

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return CronogramaSerializer
        else:
            return CronogramaCreateSerializer

    def get_queryset(self):
        return Cronograma.objects.all().order_by('-criado_em')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.order_by('-alterado_em').distinct()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(
                serializer.data
            )
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path='opcoes-etapas')
    def etapas(self, _):
        return Response(EtapasDoCronograma.etapas_to_json())
