from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from traitlets import Any

from sme_pratoaberto_terceirizadas.alimentacao.api.serializers import CardapioSerializer
from sme_pratoaberto_terceirizadas.alimentacao.api.utils import valida_usuario_vinculado_escola
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
        super(InverterDiaCardapioViewSet, self).create(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def salvar(self, request):
        if not valida_usuario_vinculado_escola(request.user):
            return Response({'details': 'Usuário sem relacionamento a uma escola'}, status=status.HTTP_409_CONFLICT)

        if InverterDiaCardapio.ja_existe(request.data):
            return Response({'details': 'Cadastro já registrado no sistema'}, status=status.HTTP_409_CONFLICT)

        if InverterDiaCardapio.salvar_solicitacao(request.data, request.user):
            return Response({'details': 'Solicitação salva com sucesso.'}, status=status.HTTP_201_CREATED)
        return Response({'details': 'Ocorreu um erro ao tentar salvar solicitação, tente novamente'}, status=status.HTTP_409_CONFLICT)
