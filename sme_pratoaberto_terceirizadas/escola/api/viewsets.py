from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import (EscolaCompletaSerializer, PeriodoEscolarSerializer, DiretoriaRegionalCompletaSerializer)
from ..models import (Escola, PeriodoEscolar, DiretoriaRegional)


class EscolaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaCompletaSerializer


class PeriodoEscolarViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = PeriodoEscolar.objects.all()
    serializer_class = PeriodoEscolarSerializer


class DiretoriaRegionalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalCompletaSerializer
