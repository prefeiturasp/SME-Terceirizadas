from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from sme_pratoaberto_terceirizadas.inclusao_alimentacao.api.serializers.serializers import (
    GrupoInclusaoAlimentacaoNormalSerializer, InclusaoAlimentacaoContinuaSerializer)
from .serializers import (EscolaCompletaSerializer, PeriodoEscolarSerializer, DiretoriaRegionalCompletaSerializer)
from ..models import (Escola, PeriodoEscolar, DiretoriaRegional)


class EscolaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaCompletaSerializer

    @action(detail=True)
    def meus_grupos_inclusao_normal(self, request, uuid=None):
        escola = self.get_object()
        inclusoes = escola.get_grupos_inclusao_normal()
        serializer = GrupoInclusaoAlimentacaoNormalSerializer(
            inclusoes, many=True
        )
        return Response(serializer.data)

    @action(detail=True)
    def minhas_inclusoes_alimentacao_continua(self, request, uuid=None):
        escola = self.get_object()
        inclusoes = escola.get_inclusoes_alimentacao_continua()
        serializer = InclusaoAlimentacaoContinuaSerializer(
            inclusoes, many=True
        )
        return Response(serializer.data)


class PeriodoEscolarViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = PeriodoEscolar.objects.all()
    serializer_class = PeriodoEscolarSerializer


class DiretoriaRegionalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalCompletaSerializer
