from rest_framework import viewsets

from .serializers import EditalSerializer, LoteSerializer
from ..models import Edital, Lote


class EditalViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalSerializer
    queryset = Edital.objects.all()


class LoteViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = LoteSerializer
    queryset = Lote.objects.all()
