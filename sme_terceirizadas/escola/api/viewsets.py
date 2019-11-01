import datetime

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .serializers import (
    DiretoriaRegionalCompletaSerializer, DiretoriaRegionalSimplissimaSerializer,
    EscolaSimplesSerializer, EscolaSimplissimaSerializer, PeriodoEscolarSerializer, SubprefeituraSerializer,
    TipoGestaoSerializer
)
from ..models import (
    Codae, DiretoriaRegional, Escola, Lote, PeriodoEscolar, Subprefeitura, TipoGestao
)
from ...escola.api.permissions import PodeCriarAdministradoresDaEscola
from ...escola.api.serializers import CODAESerializer, LoteSimplesSerializer
from ...escola.api.serializers import UsuarioDetalheSerializer
from ...escola.api.serializers_create import LoteCreateSerializer
from ...perfil.api.serializers import UsuarioUpdateSerializer, VinculoSerializer


# https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions


class VinculoEscolaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = VinculoSerializer

    @action(detail=True, permission_classes=[PodeCriarAdministradoresDaEscola], methods=['post'])
    def criar_equipe_administradora(self, request, uuid=None):
        try:
            escola = self.get_object()
            data = request.data.copy()
            data['escola'] = escola.nome
            usuario = UsuarioUpdateSerializer(request.data).create(validated_data=data)
            usuario.criar_vinculo_administrador_escola(escola)
            return Response(UsuarioDetalheSerializer(usuario).data)
        except serializers.ValidationError as e:
            return Response(data=dict(detail=e.args[0]), status=e.status_code)

    @action(detail=True, permission_classes=[PodeCriarAdministradoresDaEscola])
    def get_equipe_administradora(self, request, uuid=None):
        escola = self.get_object()
        vinculos = escola.vinculos_podem_ser_finalizados
        return Response(self.get_serializer(vinculos, many=True).data)

    @action(detail=True, permission_classes=[PodeCriarAdministradoresDaEscola], methods=['patch'])
    def finalizar_vinculo(self, request, uuid=None):
        escola = self.get_object()
        vinculo_uuid = request.data.get('vinculo_uuid')
        vinculo = escola.vinculos.get(uuid=vinculo_uuid)
        vinculo.usuario.is_active = False
        vinculo.usuario.save()
        vinculo.ativo = False
        vinculo.data_final = datetime.date.today()
        vinculo.save()
        return Response(self.get_serializer(vinculo).data)


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
