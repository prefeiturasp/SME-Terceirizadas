from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import (EscolaCompletaSerializer, PeriodoEscolarSerializer, DiretoriaRegionalCompletaSerializer)
from ..models import (Escola, PeriodoEscolar, DiretoriaRegional)


class EscolaViewSet(ReadOnlyModelViewSet):
    queryset = Escola.objects.all()
    serializer_class = EscolaCompletaSerializer


class PeriodoEscolarViewSet(ReadOnlyModelViewSet):
    queryset = PeriodoEscolar.objects.all()
    serializer_class = PeriodoEscolarSerializer


class DiretoriaRegionalViewSet(ReadOnlyModelViewSet):
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalCompletaSerializer
