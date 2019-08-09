from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from sme_pratoaberto_terceirizadas.escola.api.serializers import LoteSimplesSerializer
from sme_pratoaberto_terceirizadas.escola.api.serializers_create import LoteCreateSerializer
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.api.serializers.serializers import (
    GrupoInclusaoAlimentacaoNormalSerializer, InclusaoAlimentacaoContinuaSerializer)
from .serializers import (EscolaCompletaSerializer, PeriodoEscolarSerializer, DiretoriaRegionalCompletaSerializer,
                          TipoGestaoSerializer, SubprefeituraSerializer, EscolaSimplesSerializer,
                          DiretoriaRegionalComboSerializer, EscolaComboSerializer)
from ..models import (Escola, PeriodoEscolar, DiretoriaRegional, Lote, TipoGestao, Subprefeitura)


# https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions

class EscolaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaCompletaSerializer

    @action(detail=True)
    def meus_grupos_inclusao_normal(self, request, uuid=None):
        escola = self.get_object()
        inclusoes = escola.grupos_inclusoes.all()
        page = self.paginate_queryset(inclusoes)
        serializer = GrupoInclusaoAlimentacaoNormalSerializer(
            page, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True)
    def minhas_inclusoes_alimentacao_continua(self, request, uuid=None):
        escola = self.get_object()
        inclusoes = escola.inclusoes_continuas.all()
        page = self.paginate_queryset(inclusoes)
        serializer = InclusaoAlimentacaoContinuaSerializer(
            page, many=True
        )
        return self.get_paginated_response(serializer.data)


class EscolaSimplesViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaSimplesSerializer


class EscolaComboViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaComboSerializer


class PeriodoEscolarViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = PeriodoEscolar.objects.all()
    serializer_class = PeriodoEscolarSerializer


class DiretoriaRegionalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalCompletaSerializer


class DiretoriaRegionalComboViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalComboSerializer


class TipoGestaoViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = TipoGestao.objects.all()
    serializer_class = TipoGestaoSerializer


class SubprefeituraViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Subprefeitura.objects.all()
    serializer_class = SubprefeituraSerializer


class LoteViewSet(ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = LoteSimplesSerializer
    queryset = Lote.objects.all()

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LoteCreateSerializer
        return LoteSimplesSerializer
