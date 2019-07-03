from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import EscolaSerializer, PeriodoEscolarSerializer, DiretoriaRegionalSerializer
from ..models import Escola, PeriodoEscolar, DiretoriaRegional


class EscolaViewSet(ReadOnlyModelViewSet):
    queryset = Escola.objects.all()
    serializer_class = EscolaSerializer


class PeriodoEscolarViewSet(ReadOnlyModelViewSet):
    queryset = PeriodoEscolar.objects.all()
    serializer_class = PeriodoEscolarSerializer


class DiretoriaRegionalViewSet(ReadOnlyModelViewSet):
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalSerializer
