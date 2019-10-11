from rest_framework import viewsets
from rest_framework.decorators import action

from .constants import (
    AUTORIZADOS, CANCELADOS, FILTRO_DRE_UUID, FILTRO_ESCOLA_UUID,
    FILTRO_TERCEIRIZADA_UUID, NEGADOS, PENDENTES_APROVACAO
)
from sme_terceirizadas.paineis_consolidados.models import (
    SolicitacoesCODAE, SolicitacoesDRE, SolicitacoesEscola, SolicitacoesTerceirizada
)
from ...dados_comuns.constants import FILTRO_PADRAO_PEDIDOS, SEM_FILTRO
from ...paineis_consolidados.api.serializers import SolicitacoesSerializer


class CODAESolicitacoesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacoesCODAE.objects.all()
    serializer_class = SolicitacoesSerializer

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_APROVACAO}/{FILTRO_PADRAO_PEDIDOS}')
    def pendentes_aprovacao(self, request, filtro_aplicado=SEM_FILTRO):
        query_set = SolicitacoesCODAE.get_pendentes_autorizacao(filtro=filtro_aplicado)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=AUTORIZADOS)
    def autorizados(self, request):
        query_set = SolicitacoesCODAE.get_autorizados()
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=NEGADOS)
    def negados(self, request):
        query_set = SolicitacoesCODAE.get_negados()
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=CANCELADOS)
    def cancelados(self, request):
        query_set = SolicitacoesCODAE.get_cancelados()
        return self._retorno_base(query_set)

    def _retorno_base(self, query_set):
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class EscolaSolicitacoesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacoesEscola.objects.all()
    serializer_class = SolicitacoesSerializer

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_APROVACAO}/{FILTRO_ESCOLA_UUID}')
    def pendentes_aprovacao(self, request, escola_uuid=None):
        query_set = SolicitacoesEscola.get_pendentes_autorizacao(escola_uuid=escola_uuid)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS}/{FILTRO_ESCOLA_UUID}')
    def autorizados(self, request, escola_uuid=None):
        query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola_uuid)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS}/{FILTRO_ESCOLA_UUID}')
    def negados(self, request, escola_uuid=None):
        query_set = SolicitacoesEscola.get_negados(escola_uuid=escola_uuid)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS}/{FILTRO_ESCOLA_UUID}')
    def cancelados(self, request, escola_uuid=None):
        query_set = SolicitacoesEscola.get_cancelados(escola_uuid=escola_uuid)
        return self._retorno_base(query_set)

    def _retorno_base(self, query_set):
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class DRESolicitacoesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacoesDRE.objects.all()
    serializer_class = SolicitacoesSerializer

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_APROVACAO}/{FILTRO_DRE_UUID}')
    def pendentes_aprovacao(self, request, dre_uuid=None):
        query_set = SolicitacoesDRE.get_pendentes_autorizacao(dre_uuid=dre_uuid)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{AUTORIZADOS}/{FILTRO_DRE_UUID}')
    def autorizados(self, request, dre_uuid=None):
        query_set = SolicitacoesDRE.get_autorizados(dre_uuid=dre_uuid)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{NEGADOS}/{FILTRO_DRE_UUID}')
    def negados(self, request, dre_uuid=None):
        query_set = SolicitacoesDRE.get_negados(dre_uuid=dre_uuid)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS}/{FILTRO_DRE_UUID}')
    def cancelados(self, request, dre_uuid=None):
        query_set = SolicitacoesDRE.get_cancelados(dre_uuid=dre_uuid)
        return self._retorno_base(query_set)

    def _retorno_base(self, query_set):
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TerceirizadaSolicitacoesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacoesTerceirizada.objects.all()
    serializer_class = SolicitacoesSerializer

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_APROVACAO}/{FILTRO_TERCEIRIZADA_UUID}')
    def pendentes_aprovacao(self, request, terceirizada_uuid=None):
        query_set = SolicitacoesTerceirizada.get_pendentes_autorizacao(terceirizada_uuid=terceirizada_uuid)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=f'{CANCELADOS}/{FILTRO_TERCEIRIZADA_UUID}')
    def cancelados(self, request, terceirizada_uuid=None):
        query_set = SolicitacoesTerceirizada.get_cancelados(terceirizada_uuid=terceirizada_uuid)
        return self._retorno_base(query_set)

    def _retorno_base(self, query_set):
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
