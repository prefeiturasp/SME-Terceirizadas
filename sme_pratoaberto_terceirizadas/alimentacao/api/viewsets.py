from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from traitlets import Any

from sme_pratoaberto_terceirizadas.alimentacao.api.serializers import CardapioSerializer
from sme_pratoaberto_terceirizadas.alimentacao.api.utils import converter_str_para_datetime
from sme_pratoaberto_terceirizadas.alimentacao.api.validators import validacao_e_solicitacao, validacao_e_salvamento
from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio, InverterDiaCardapio
from sme_pratoaberto_terceirizadas.school.models import School
from .serializers import InverterDiaCardapioSerializer


class CardapioViewSet(viewsets.ModelViewSet):
    """ Endpoint com os cardápios cadastrados """
    queryset = Cardapio.objects.all()
    serializer_class = CardapioSerializer


class InverterDiaCardapioViewSet(viewsets.ModelViewSet):
    """ Endpoint para solicitar inversão para dia de cardápio """
    queryset = InverterDiaCardapio.objects.filter(status='ESCOLA_SALVOU')
    serializer_class = InverterDiaCardapioSerializer
    lookup_field = 'uuid'

    def create(self, request: Request, *args, **kwargs):
        request = self._filters(request)
        return validacao_e_solicitacao(request)

    def destroy(self, request: Request, *args: Any, **kwargs: Any):
        response = super(InverterDiaCardapioViewSet, self).destroy(request)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'details': 'Solicitação removida com sucesso.'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'details': 'Error ao tentar remover solicitação '}, status=status.HTTP_409_CONFLICT)

    @action(detail=False, methods=['post'])
    def salvar(self, request):
        request = self._filters(request)
        return validacao_e_salvamento(request)

    def _filters(self, request):
        request.data['data_de'] = converter_str_para_datetime(request.data.get('data_de'), formato='%d/%m/%Y')
        request.data['data_para'] = converter_str_para_datetime(request.data.get('data_para'), formato='%d/%m/%Y')
        request.data['escola'] = School.get_escola_by_usuario(request.user)
        return request
