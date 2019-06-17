from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from traitlets import Any

from sme_pratoaberto_terceirizadas.alimentacao.api.serializers import CardapioSerializer
from sme_pratoaberto_terceirizadas.alimentacao.api.utils import valida_usuario_vinculado_escola, notifica_dres
from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio, InverterDiaCardapio, StatusSolicitacoes
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

    def create(self, request: Request, *args: Any, **kwargs: Any):
        response = super(InverterDiaCardapioViewSet, self).create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            params = response.data
            notifica_dres(request.user, params.get('escola'), params.get('data_de'), params.get('data_para'))
            return Response({'details': 'Solicitação enviada com sucesso.'}, status=status.HTTP_200_OK)
        return Response({'details': 'Error ao tentar solicitar inversão de dia de cardápio'})
    
    def destroy(self, request: Request, *args: Any, **kwargs: Any):
        response = super(InverterDiaCardapioViewSet, self).destroy(request)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'details': 'Solicitação removida com sucesso.'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'details': 'Error ao tentar remover solicitação '}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def salvar(self, request):
        if not valida_usuario_vinculado_escola(request.user):
            return Response({'details': 'Usuário sem relacionamento a uma escola'}, status=status.HTTP_409_CONFLICT)
        if InverterDiaCardapio.salvar_solicitacao(request.data, request.user):
            return Response({'details': 'Solicitação salva com sucesso.'}, status=status.HTTP_201_CREATED)
        return Response({'details': 'Ocorreu um erro ao tentar salvar solicitação, tente novamente'},
                        status=status.HTTP_409_CONFLICT)

