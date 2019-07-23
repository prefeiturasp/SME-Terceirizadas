from rest_framework import viewsets

from .serializers import EditalSerializer
from ..models import Edital


class EditalViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalSerializer
    queryset = Edital.objects.all()
