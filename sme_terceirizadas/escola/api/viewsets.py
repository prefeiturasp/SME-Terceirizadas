from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from sme_terceirizadas.escola.api.permissions import PodeCriarAdministradoresDaEscola
from .serializers import (
    DiretoriaRegionalCompletaSerializer, DiretoriaRegionalSimplissimaSerializer, EscolaCompletaSerializer,
    EscolaSimplesSerializer, EscolaSimplissimaSerializer, PeriodoEscolarSerializer, SubprefeituraSerializer,
    TipoGestaoSerializer
)
from ..models import (
    Codae, DiretoriaRegional, Escola, Lote, PeriodoEscolar, Subprefeitura, TipoGestao
)
from ...escola.api.serializers import CODAESerializer, LoteSimplesSerializer
from ...escola.api.serializers_create import LoteCreateSerializer
from ...inclusao_alimentacao.api.serializers.serializers import (
    GrupoInclusaoAlimentacaoNormalSerializer, InclusaoAlimentacaoContinuaSerializer
)


# https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions


class EscolaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaCompletaSerializer

    @action(detail=True, permission_classes=[PodeCriarAdministradoresDaEscola], methods=['post'])
    def criar_equipe_administradora(self, request, uuid=None):
        pass

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


class EscolaSimplissimaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaSimplissimaSerializer


class PeriodoEscolarViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = PeriodoEscolar.objects.all()
    serializer_class = PeriodoEscolarSerializer


class DiretoriaRegionalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalCompletaSerializer


class DiretoriaRegionalSimplissimaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalSimplissimaSerializer


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

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LoteCreateSerializer
        return LoteSimplesSerializer

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Não é permitido excluir um Lote com escolas associadas'},
                        status=status.HTTP_401_UNAUTHORIZED)


class CODAESimplesViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Codae.objects.all()
    serializer_class = CODAESerializer
