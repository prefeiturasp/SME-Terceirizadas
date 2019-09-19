from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models.codae import SolicitacoesCODAE
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

    @action(detail=False, methods=['GET'], url_path='pendentes-aprovacao')
    def pendentes_aprovacao(self, request):
        query_set = SolicitacoesCODAE.get_pendentes_aprovacao()
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='aprovados')
    def aprovados(self, request):
        query_set = SolicitacoesCODAE.get_autorizados()
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='cancelados')
    def cancelados(self, request):
        query_set = SolicitacoesCODAE.get_negados()
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='solicitacoes-revisao')
    def solicitacoes_revisao(self, request):
        query_set = SolicitacoesCODAE.get_solicitacoes_revisao()
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
