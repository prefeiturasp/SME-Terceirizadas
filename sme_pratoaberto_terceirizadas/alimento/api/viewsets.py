from rest_framework import viewsets

from sme_pratoaberto_terceirizadas.alimento.api.serializers import RefeicaoSerializer
from sme_pratoaberto_terceirizadas.alimento.models import Refeicao


class RefeicaoViewSet(viewsets.ModelViewSet):
    queryset = Refeicao.objects.all()
    serializer_class = RefeicaoSerializer
