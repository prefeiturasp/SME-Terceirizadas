from rest_framework import viewsets

from .serializers.serializers import CardapioSerializer, TipoAlimentacaoSerializer, InversaoCardapioSerializer
from ..models import Cardapio, TipoAlimentacao, InversaoCardapio
from sme_pratoaberto_terceirizadas.cardapio.api.serializers.serializers_create import InversaoCardapioSerializerCreate


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
    queryset = InversaoCardapio.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InversaoCardapioSerializerCreate
        return InversaoCardapioSerializer
