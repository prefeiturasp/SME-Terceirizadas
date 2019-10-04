from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .constants import (
    AUTORIZADOS, CANCELADOS, FILTRO_DRE_UUID, FILTRO_ESCOLA_UUID, NEGADOS, PENDENTES_APROVACAO, _NEGADOS
)
from ..models.codae import (
    SolicitacoesCODAE, SolicitacoesDRE, SolicitacoesEscola
)
from ...dados_comuns.constants import FILTRO_PADRAO_PEDIDOS, SEM_FILTRO
from ...escola.models import DiretoriaRegional
from ...paineis_consolidados.api.serializers import SolicitacoesSerializer


class DrePendentesAprovacaoViewSet(viewsets.ViewSet):

    def list(self, request):
        usuario = request.user
        # TODO Rever quando a regra de negócios de perfis estiver definida.
        dre = DiretoriaRegional.objects.filter(usuarios=usuario).first()
        response = []
        for alteracao in dre.alteracoes_cardapio_pendentes_das_minhas_escolas.all():
            nova_alteracao = {
                'text': f'{alteracao.id_externo} - {alteracao.escola.lote} - Alteração de Cardápio',
                'date': f'{alteracao.data_inicial}'
            }

            response.append(nova_alteracao)

        return Response(response, status=status.HTTP_200_OK)


class CODAESolicitacoesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacoesCODAE.objects.all()
    serializer_class = SolicitacoesSerializer

    @action(detail=False, methods=['GET'], url_path=f'{PENDENTES_APROVACAO}/{FILTRO_PADRAO_PEDIDOS}')
    def pendentes_aprovacao(self, request, filtro_aplicado=SEM_FILTRO):
        query_set = SolicitacoesCODAE.get_pendentes_aprovacao(filtro=filtro_aplicado)
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=AUTORIZADOS)
    def aprovados(self, request):
        query_set = SolicitacoesCODAE.get_autorizados()
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path='solicitacoes-revisao')
    def solicitacoes_revisao(self, request):
        query_set = SolicitacoesCODAE.get_solicitacoes_revisao()
        return self._retorno_base(query_set)

    @action(detail=False, methods=['GET'], url_path=_NEGADOS)
    def cancelados(self, request):
        query_set = SolicitacoesCODAE.get_negados()
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
        query_set = SolicitacoesEscola.get_pendentes_aprovacao(escola_uuid=escola_uuid)
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
        query_set = SolicitacoesDRE.get_pendentes_aprovacao(dre_uuid=dre_uuid)
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
