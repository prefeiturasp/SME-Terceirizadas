from rest_framework import viewsets

from .serializers.serializers import (
    EditalSerializer, TerceirizadaSerializer, EditalContratosSerializer
)
from .serializers.serializers_create import TerceirizadaCreateSerializer
from ..models import Edital, Terceirizada


class EditalViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalSerializer
    queryset = Edital.objects.all()


class TerceirizadaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = TerceirizadaSerializer
    queryset = Terceirizada.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TerceirizadaCreateSerializer
        return TerceirizadaSerializer


class EditalContratosViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalContratosSerializer
    queryset = Edital.objects.all()
