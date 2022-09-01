from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from ...dados_comuns.permissions import UsuarioEscola, ViewSetActionPermissionMixin
from ...escola.api.permissions import PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada
from ..models import (
    CategoriaMedicao,
    DiaSobremesaDoce,
    Medicao,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)
from .permissions import EhAdministradorMedicaoInicialOuGestaoAlimentacao
from .serializers import (
    CategoriaMedicaoSerializer,
    DiaSobremesaDoceSerializer,
    SolicitacaoMedicaoInicialSerializer,
    TipoContagemAlimentacaoSerializer,
    ValorMedicaoSerializer
)
from .serializers_create import (
    DiaSobremesaDoceCreateManySerializer,
    MedicaoCreateUpdateSerializer,
    SolicitacaoMedicaoInicialCreateSerializer
)


class DiaSobremesaDoceViewSet(ViewSetActionPermissionMixin, ModelViewSet):
    permission_action_classes = {
        'list': [EhAdministradorMedicaoInicialOuGestaoAlimentacao],
        'create': [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada],
        'delete': [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada]
    }
    queryset = DiaSobremesaDoce.objects.all()
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DiaSobremesaDoceCreateManySerializer
        return DiaSobremesaDoceSerializer

    def get_queryset(self):
        queryset = DiaSobremesaDoce.objects.all()
        if 'mes' in self.request.query_params and 'ano' in self.request.query_params:
            queryset = queryset.filter(data__month=self.request.query_params.get('mes'),
                                       data__year=self.request.query_params.get('ano'))
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super(DiaSobremesaDoceViewSet, self).create(request, *args, **kwargs)
        except AssertionError as error:
            if str(error) == '`create()` did not return an object instance.':
                return Response(status=status.HTTP_201_CREATED)
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)


class SolicitacaoMedicaoInicialViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = (UsuarioEscola,)
    queryset = SolicitacaoMedicaoInicial.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitacaoMedicaoInicialCreateSerializer
        return SolicitacaoMedicaoInicialSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        escola_uuid = request.query_params.get('escola')
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')

        queryset = queryset.filter(escola__uuid=escola_uuid, mes=mes, ano=ano)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TipoContagemAlimentacaoViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = TipoContagemAlimentacao.objects.filter(ativo=True)
    serializer_class = TipoContagemAlimentacaoSerializer
    pagination_class = None


class CategoriaMedicaoViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = CategoriaMedicao.objects.filter(ativo=True)
    serializer_class = CategoriaMedicaoSerializer
    pagination_class = None


class ValorMedicaoViewSet(
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    queryset = ValorMedicao.objects.all()
    serializer_class = ValorMedicaoSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = ValorMedicao.objects.all()
        nome_periodo_escolar = self.request.query_params.get('nome_periodo_escolar', '')
        uuid_solicitacao_medicao = self.request.query_params.get('uuid_solicitacao_medicao', '')
        if nome_periodo_escolar:
            queryset = queryset.filter(medicao__periodo_escolar__nome=nome_periodo_escolar)
        if uuid_solicitacao_medicao:
            queryset = queryset.filter(medicao__solicitacao_medicao_inicial__uuid=uuid_solicitacao_medicao)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        medicao = instance.medicao
        self.perform_destroy(instance)
        if not medicao.valores_medicao.all().exists():
            medicao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MedicaoViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    queryset = Medicao.objects.all()

    def get_serializer_class(self):
        return MedicaoCreateUpdateSerializer
