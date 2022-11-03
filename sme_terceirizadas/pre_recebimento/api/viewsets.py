
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sme_terceirizadas.pre_recebimento.api.serializers.serializer_create import CronogramaCreateSerializer
from sme_terceirizadas.pre_recebimento.api.serializers.serializers import CronogramaSerializer
from sme_terceirizadas.pre_recebimento.models import Cronograma, EtapasDoCronograma


class CronogramaModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Cronograma.objects.all()
    serializer_class = CronogramaSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return CronogramaSerializer
        else:
            return CronogramaCreateSerializer

    @action(detail=False, url_path='opcoes-etapas')
    def etapas(self, _):
        return Response(EtapasDoCronograma.etapas_to_json())
