from rest_framework import viewsets

from .serializers import CardapioSerializer
from ..models import Cardapio


class CardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = CardapioSerializer
    queryset = Cardapio.objects.all().order_by('data')
