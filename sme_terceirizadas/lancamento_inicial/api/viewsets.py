from rest_framework.viewsets import ModelViewSet

from ..models import LancamentoDiario, Refeicao
from .serializers import LancamentoDiarioSerializer, RefeicaoSerializer

class LancamentoDiarioViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = LancamentoDiario.objects.all()
    serializer_class = LancamentoDiarioSerializer
