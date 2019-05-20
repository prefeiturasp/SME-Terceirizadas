from rest_framework.viewsets import ModelViewSet

from .serializers import AlteracaoCardapioSerializer
from ..models import AlteracaoCardapio


class AlteracaoCardapioViewSet(ModelViewSet):
    queryset = AlteracaoCardapio.objects.all()
    serializer_class = AlteracaoCardapioSerializer
