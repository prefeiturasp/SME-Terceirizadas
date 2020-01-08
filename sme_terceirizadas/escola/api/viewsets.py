from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from ...dados_comuns.constants import (
    ADMINISTRADOR_DRE,
    ADMINISTRADOR_ESCOLA,
    ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA
)
from ...escola.api.permissions import (
    PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada,
    PodeCriarAdministradoresDaDiretoriaRegional,
    PodeCriarAdministradoresDaEscola
)
from ...escola.api.serializers import CODAESerializer, LoteSimplesSerializer, UsuarioDetalheSerializer
from ...escola.api.serializers_create import LoteCreateSerializer
from ...paineis_consolidados.api.constants import FILTRO_DRE_UUID
from ...perfil.api.serializers import UsuarioUpdateSerializer, VinculoSerializer
from ..models import (
    Codae,
    DiretoriaRegional,
    Escola,
    Lote,
    PeriodoEscolar,
    Subprefeitura,
    TipoGestao,
    TipoUnidadeEscolar
)
from .serializers import (
    DiretoriaRegionalCompletaSerializer,
    DiretoriaRegionalSimplissimaSerializer,
    EscolaSimplesSerializer,
    EscolaSimplissimaSerializer,
    PeriodoEscolarSerializer,
    SubprefeituraSerializer,
    TipoGestaoSerializer,
    TipoUnidadeEscolarSerializer
)


# https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions


class VinculoEscolaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    permission_classes = [PodeCriarAdministradoresDaEscola]
    serializer_class = VinculoSerializer

    @action(detail=True, methods=['post'])
    def criar_equipe_administradora(self, request, uuid=None):
        try:
            escola = self.get_object()
            data = request.data.copy()
            data['instituicao'] = escola.nome
            usuario = UsuarioUpdateSerializer(data).create(validated_data=data)
            usuario.criar_vinculo_administrador(escola, nome_perfil=ADMINISTRADOR_ESCOLA)
            return Response(UsuarioDetalheSerializer(usuario).data)
        except serializers.ValidationError as e:
            return Response(data=dict(detail=e.args[0]), status=e.status_code)

    @action(detail=True)
    def get_equipe_administradora(self, request, uuid=None):
        escola = self.get_object()
        vinculos = escola.vinculos_que_podem_ser_finalizados
        return Response(self.get_serializer(vinculos, many=True).data)

    @action(detail=True, methods=['patch'])
    def finalizar_vinculo(self, request, uuid=None):
        escola = self.get_object()
        vinculo_uuid = request.data.get('vinculo_uuid')
        vinculo = escola.vinculos.get(uuid=vinculo_uuid)
        vinculo.finalizar_vinculo()
        return Response(self.get_serializer(vinculo).data)


class VinculoDiretoriaRegionalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = DiretoriaRegional.objects.all()
    serializer_class = VinculoSerializer
    permission_classes = [PodeCriarAdministradoresDaDiretoriaRegional]

    @action(detail=True, methods=['post'])
    def criar_equipe_administradora(self, request, uuid=None):
        try:
            diretoria_regional = self.get_object()
            data = request.data.copy()
            data['instituicao'] = diretoria_regional.nome
            usuario = UsuarioUpdateSerializer(data).create(validated_data=data)
            usuario.criar_vinculo_administrador(diretoria_regional, nome_perfil=ADMINISTRADOR_DRE)
            return Response(UsuarioDetalheSerializer(usuario).data)
        except serializers.ValidationError as e:
            return Response(data=dict(detail=e.args[0]), status=e.status_code)

    @action(detail=True)
    def get_equipe_administradora(self, request, uuid=None):
        diretoria_regional = self.get_object()
        vinculos = diretoria_regional.vinculos_que_podem_ser_finalizados
        return Response(self.get_serializer(vinculos, many=True).data)

    @action(detail=True, methods=['patch'])
    def finalizar_vinculo(self, request, uuid=None):
        diretoria_regional = self.get_object()
        vinculo_uuid = request.data.get('vinculo_uuid')
        vinculo = diretoria_regional.vinculos.get(uuid=vinculo_uuid)
        vinculo.finalizar_vinculo()
        return Response(self.get_serializer(vinculo).data)


class VinculoCODAEGestaoAlimentacaoTerceirizadaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Codae.objects.all()
    serializer_class = VinculoSerializer
    permission_classes = [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada]

    @action(detail=True, methods=['post'])
    def criar_equipe_administradora(self, request, uuid=None):
        try:
            codae = self.get_object()
            data = request.data.copy()
            data['instituicao'] = codae.nome
            usuario = UsuarioUpdateSerializer(data).create(validated_data=data)
            usuario.criar_vinculo_administrador(codae, nome_perfil=ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA)
            return Response(UsuarioDetalheSerializer(usuario).data)
        except serializers.ValidationError as e:
            return Response(data=dict(detail=e.args[0]), status=e.status_code)

    @action(detail=True)
    def get_equipe_administradora(self, request, uuid=None):
        codae = self.get_object()
        vinculos = codae.vinculos_que_podem_ser_finalizados
        return Response(self.get_serializer(vinculos, many=True).data)

    @action(detail=True, methods=['patch'])
    def finalizar_vinculo(self, request, uuid=None):
        codae = self.get_object()
        vinculo_uuid = request.data.get('vinculo_uuid')
        vinculo = codae.vinculos.get(uuid=vinculo_uuid)
        vinculo.finalizar_vinculo()
        return Response(self.get_serializer(vinculo).data)


class EscolaSimplesViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaSimplesSerializer


class EscolaSimplissimaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Escola.objects.all()
    serializer_class = EscolaSimplissimaSerializer

    @action(detail=False, methods=['GET'], url_path=f'{FILTRO_DRE_UUID}')
    def filtro_por_diretoria_regional(self, request, dre_uuid=None):
        escolas = Escola.objects.filter(diretoria_regional__uuid=dre_uuid)
        return Response(self.get_serializer(escolas, many=True).data)


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


class TipoUnidadeEscolarViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = TipoUnidadeEscolarSerializer
    queryset = TipoUnidadeEscolar.objects.all()
