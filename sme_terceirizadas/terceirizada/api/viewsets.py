from django.db.models import Q
from django.db.models.functions import Lower
from django_filters import rest_framework as filters
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from ...escola.api.serializers import TerceirizadaSerializer, UsuarioDetalheSerializer
from ...perfil.api.serializers import UsuarioUpdateSerializer, VinculoSerializer
from ...relatorios.relatorios import relatorio_quantitativo_por_terceirizada
from ..forms import RelatorioQuantitativoForm
from ..models import Contrato, Edital, EmailTerceirizadaPorModulo, Terceirizada
from ..utils import TerceirizadasEmailsPagination, obtem_dados_relatorio_quantitativo
from .filters import EmailTerceirizadaPorModuloFilter, TerceirizadaFilter
from .permissions import PodeCriarAdministradoresDaTerceirizada
from .serializers.serializers import (
    ContratoSerializer,
    DistribuidorSimplesSerializer,
    EditalContratosSerializer,
    EditalSerializer,
    EditalSimplesSerializer,
    EmailsPorModuloSerializer,
    EmailsTerceirizadaPorModuloSerializer,
    TerceirizadaLookUpSerializer,
    TerceirizadaSimplesSerializer
)
from .serializers.serializers_create import (
    CreateEmailTerceirizadaPorModuloSerializer,
    EditalContratosCreateSerializer,
    EmpresaNaoTerceirizadaCreateSerializer,
    TerceirizadaCreateSerializer
)


class EditalViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalSerializer
    queryset = Edital.objects.all()

    @action(detail=False, methods=['GET'], url_path='lista-numeros')
    def lista_numeros(self, request):
        queryset = self.get_queryset()
        response = {'results': EditalSimplesSerializer(queryset, many=True).data}
        return Response(response)


class EmpresaNaoTerceirizadaViewSet(viewsets.mixins.CreateModelMixin,
                                    viewsets.mixins.UpdateModelMixin,
                                    viewsets.mixins.DestroyModelMixin,
                                    viewsets.GenericViewSet):
    lookup_field = 'uuid'
    queryset = Terceirizada.objects.all().order_by(Lower('razao_social'))
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TerceirizadaFilter
    serializer_class = EmpresaNaoTerceirizadaCreateSerializer


class TerceirizadaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Terceirizada.objects.all().order_by(Lower('razao_social'))
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TerceirizadaFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TerceirizadaCreateSerializer
        return TerceirizadaSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_nomes(self, request):
        response = {'results': TerceirizadaSimplesSerializer(self.filter_queryset(self.get_queryset()), many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-nomes-distribuidores')
    def lista_nomes_distribuidores(self, request):
        queryset = Terceirizada.objects.filter(tipo_servico=Terceirizada.DISTRIBUIDOR_ARMAZEM)
        response = {'results': DistribuidorSimplesSerializer(queryset, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-fornecedores-simples')
    def lista_fornecedores_simples(self, request):
        queryset = Terceirizada.objects.filter(tipo_servico=Terceirizada.FORNECEDOR)
        response = {'results': TerceirizadaSimplesSerializer(queryset, many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-cnpjs')
    def lista_cnpjs(self, request):
        queryset = Terceirizada.objects.all().values_list('cnpj', flat=True)
        response = {'results': queryset}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='relatorio-quantitativo')
    def relatorio_quantitativo(self, request):
        form = RelatorioQuantitativoForm(request.GET)

        if not form.is_valid():
            return Response(form.errors)

        return Response(obtem_dados_relatorio_quantitativo(form.cleaned_data))

    @action(detail=False, methods=['GET'], url_path='imprimir-relatorio-quantitativo')
    def imprimir_relatorio_quantitativo(self, request):
        form = RelatorioQuantitativoForm(request.GET)

        if not form.is_valid():
            return Response(form.errors)

        dados_relatorio = obtem_dados_relatorio_quantitativo(form.cleaned_data)

        return relatorio_quantitativo_por_terceirizada(
            self.request, form.cleaned_data, dados_relatorio)

    @action(
        detail=False, methods=['GET'],
        url_path='emails-por-modulo')
    def emails_por_modulo(self, request):
        modulo = request.query_params.get('modulo', None)
        busca = request.query_params.get('busca', None)
        queryset = Terceirizada.objects.filter(emails_terceirizadas__modulo__nome=modulo).distinct(
            'razao_social').order_by('razao_social')
        self.pagination_class = TerceirizadasEmailsPagination
        if busca:
            queryset = queryset.filter(Q(emails_terceirizadas__email__icontains=busca) |
                                       Q(razao_social__icontains=busca))
        page = self.paginate_queryset(queryset)
        serializer = EmailsPorModuloSerializer(
            page if page is not None else queryset, many=True, context={'busca': busca})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='lista-razoes')
    def lista_razoes(self, request):
        response = {'results': TerceirizadaLookUpSerializer(self.get_queryset(), many=True).data}
        return Response(response)


class EditalContratosViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalContratosSerializer
    queryset = Edital.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EditalContratosCreateSerializer
        return EditalContratosSerializer


class VinculoTerceirizadaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Terceirizada.objects.all()
    permission_classes = [PodeCriarAdministradoresDaTerceirizada]
    serializer_class = VinculoSerializer

    @action(detail=True, methods=['post'])
    def criar_equipe_administradora(self, request, uuid=None):
        try:
            terceirizada = self.get_object()
            usuario = UsuarioUpdateSerializer().create_nutricionista(terceirizada=terceirizada,
                                                                     validated_data=request.data)
            return Response(UsuarioDetalheSerializer(usuario).data)
        except serializers.ValidationError as e:
            return Response(data=dict(detail=e.args[0]), status=e.status_code)

    @action(detail=True)
    def get_equipe_administradora(self, request, uuid=None):
        terceirizada = self.get_object()
        vinculos = terceirizada.vinculos_que_podem_ser_finalizados
        return Response(self.get_serializer(vinculos, many=True).data)

    @action(detail=True, methods=['patch'])
    def finalizar_vinculo(self, request, uuid=None):
        try:
            terceirizada = self.get_object()
            vinculo_uuid = request.data.get('vinculo_uuid')
            vinculo = terceirizada.vinculos.get(uuid=vinculo_uuid)
            assert vinculo.usuario.super_admin_terceirizadas is False, 'Não pode excluir usuário Administrador'
            vinculo.finalizar_vinculo()
            return Response(self.get_serializer(vinculo).data)
        except AssertionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmailTerceirizadaPorModuloViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EmailsTerceirizadaPorModuloSerializer
    queryset = EmailTerceirizadaPorModulo.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EmailTerceirizadaPorModuloFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateEmailTerceirizadaPorModuloSerializer
        return EmailsTerceirizadaPorModuloSerializer


class ContratoViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = ContratoSerializer
    queryset = Contrato.objects.all()

    @action(detail=True, methods=['patch'], url_path='encerrar-contrato')
    def encerrar_contrato(self, request, uuid=None):
        contrato = self.get_object()

        try:
            dados_encerramento = Contrato.encerra_contrato(uuid=contrato.uuid)
        except Exception as err:
            return Response(dict(detail=f'Erro ao encerrar contrato: {err}'), status=status.HTTP_400_BAD_REQUEST)

        return Response(dados_encerramento, status=status.HTTP_200_OK)
