from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .serializers import serializers
from .serializers import serializers_create
from .. import models


class MotivoSolicitacaoUnificadaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.MotivoSolicitacaoUnificada.objects.all()
    serializer_class = serializers.MotivoSolicitacaoUnificadaSerializer


class KitLancheViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = models.KitLanche.objects.all()
    serializer_class = serializers.KitLancheSerializer


class SolicitacaoKitLancheAvulsaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.SolicitacaoKitLancheAvulsa.objects.all()
    serializer_class = serializers.SolicitacaoKitLancheAvulsaSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers_create.SolicitacaoKitLancheAvulsaCreationSerializer
        return serializers.SolicitacaoKitLancheAvulsaSerializer


class SolicitacaoKitLancheUnificadaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.SolicitacaoKitLancheUnificada.objects.all()
    serializer_class = serializers.SolicitacaoKitLancheUnificadaSerializer
