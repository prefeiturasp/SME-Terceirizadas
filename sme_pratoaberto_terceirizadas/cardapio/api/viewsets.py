from rest_framework import viewsets

from .serializers import (
    CardapioSerializer, TipoAlimentacaoSerializer,
    InversaoCardapioSerializer, SuspensaoAlimentacaoSerializer
)
from .serializers_create import (
    InversaoCardapioSerializerCreate, CardapioCreateSerializer,
    SuspensaoAlimentacaoCreateSerializer
)
from ..models import Cardapio, TipoAlimentacao, InversaoCardapio
from ..models import SuspensaoAlimentacao


class CardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = CardapioSerializer
    queryset = Cardapio.objects.all().order_by('data')

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CardapioCreateSerializer
        return CardapioSerializer


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


class SuspensaoAlimentacaoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = SuspensaoAlimentacao.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SuspensaoAlimentacaoCreateSerializer
        return SuspensaoAlimentacaoSerializer
