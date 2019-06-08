from rest_framework import viewsets

from sme_pratoaberto_terceirizadas.alimentacao.api.serializers import CardapioSerializer
from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio


class CardapioViewSet(viewsets.ModelViewSet):
    queryset = Cardapio.objects.all()
    serializer_class = CardapioSerializer

