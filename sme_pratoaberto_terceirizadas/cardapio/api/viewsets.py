from rest_framework import viewsets

from .serializers import CardapioSerializer, TipoAlimentacaoSerializer, InversaoCardapioSerializer
from ..models import Cardapio, TipoAlimentacao, InversaoCardapio


class CardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = CardapioSerializer
    queryset = Cardapio.objects.all().order_by('data')


class TipoAlimentacaoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = TipoAlimentacaoSerializer
    queryset = TipoAlimentacao.objects.all()


class InversaoCardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = InversaoCardapioSerializer
    queryset = InversaoCardapio.objects.all()
