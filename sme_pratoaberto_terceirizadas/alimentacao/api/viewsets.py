from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from traitlets import Any

from sme_pratoaberto_terceirizadas.alimentacao.api.serializers import CardapioSerializer
from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio, InverterDiaCardapio, StatusSolicitacoes
from .serializers import InverterDiaCardapioSerializer


class CardapioViewSet(viewsets.ModelViewSet):
    """ Endpoint com os cardápios cadastrados """
    queryset = Cardapio.objects.all()
    serializer_class = CardapioSerializer


class InverterDiaCardapioViewSet(viewsets.ModelViewSet):
    """ Endpoint para solicitar inversão para dia de cardápio """
    queryset = InverterDiaCardapio.objects.all()
    serializer_class = InverterDiaCardapioSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any):
        if request.data.get('acao') == 'SALVAR':
            request.data['acao'] = StatusSolicitacoes.ESCOLA_SALVOU
            if InverterDiaCardapio.salvar_solicitacao(request.data):
                return Response({'details': 'Solicitação salva com sucesso.'})
        super(InverterDiaCardapioViewSet, self).create(request, *args, **kwargs)
