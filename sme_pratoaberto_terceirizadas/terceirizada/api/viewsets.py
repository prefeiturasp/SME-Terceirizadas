from rest_framework import viewsets

from .serializers.serializers import (
    EditalSerializer, TerceirizadaSerializer
)
from ..models import Edital, Terceirizada


class EditalViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalSerializer
    queryset = Edital.objects.all()


class TerceirizadaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = TerceirizadaSerializer
    queryset = Terceirizada.objects.all()
