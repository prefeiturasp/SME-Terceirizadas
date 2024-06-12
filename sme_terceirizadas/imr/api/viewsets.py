from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sme_terceirizadas.dados_comuns.api.paginations import DefaultPagination
from sme_terceirizadas.dados_comuns.permissions import (
    UsuarioCODAENutriSupervisao,
    UsuarioEscolaTercTotal,
)
from sme_terceirizadas.terceirizada.models import Edital

from ...dados_comuns.fluxo_status import FormularioSupervisaoWorkflow
from ..models import (
    Equipamento,
    FormularioSupervisao,
    Insumo,
    Mobiliario,
    PeriodoVisita,
    ReparoEAdaptacao,
    TipoOcorrencia,
    UtensilioCozinha,
    UtensilioMesa,
)
from .filters import FormularioSupervisaoFilter
from .serializers.serializers import (
    EquipamentoSerializer,
    FormularioSupervisaoSerializer,
    FormularioSupervisaoSimplesSerializer,
    InsumoSerializer,
    MobiliarioSerializer,
    PeriodoVisitaSerializer,
    ReparoEAdaptacaoSerializer,
    TipoOcorrenciaSerializer,
    UtensilioCozinhaSerializer,
    UtensilioMesaSerializer,
)
from .serializers.serializers_create import (
    FormularioDiretorManyCreateSerializer,
    FormularioSupervisaoCreateSerializer,
    FormularioSupervisaoRascunhoCreateSerializer,
)


class PeriodoVisitaModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = PeriodoVisita.objects.all().order_by("-criado_em")
    permission_classes = (UsuarioCODAENutriSupervisao,)
    serializer_class = PeriodoVisitaSerializer
    pagination_class = DefaultPagination


class FormularioSupervisaoRascunhoModelViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    lookup_field = "uuid"
    queryset = FormularioSupervisao.objects.all().order_by("-criado_em")
    permission_classes = (UsuarioCODAENutriSupervisao,)
    serializer_class = FormularioSupervisaoRascunhoCreateSerializer
    pagination_class = DefaultPagination


class FormularioSupervisaoModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
):
    lookup_field = "uuid"
    queryset = FormularioSupervisao.objects.all().order_by("-criado_em")
    permission_classes = (UsuarioCODAENutriSupervisao,)
    serializer_class = FormularioSupervisaoSerializer
    pagination_class = DefaultPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FormularioSupervisaoFilter

    def get_serializer_class(self):
        return {
            "list": FormularioSupervisaoSimplesSerializer,
            "retrieve": FormularioSupervisaoSerializer,
        }.get(self.action, FormularioSupervisaoCreateSerializer)

    @action(
        detail=False,
        url_path="tipos-ocorrencias",
    )
    def tipos_ocorrencias(self, request):
        edital_uuid = request.query_params.get("edital_uuid")

        try:
            edital = Edital.objects.get(uuid=edital_uuid)
        except Edital.DoesNotExist:
            return Response(
                {
                    "detail": "Edital do tipo IMR com o UUID informado não foi encontrado."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        queryset = TipoOcorrencia.para_nutrisupervisores.filter(edital=edital)

        serializer = TipoOcorrenciaSerializer(queryset, many=True)

        return Response(serializer.data)

    def formatar_filtros(self, query_params):
        kwargs = {}
        if query_params.get("dre"):
            kwargs["escola__lote__diretoria_regional__uuid"] = query_params.get("dre")
        if query_params.get("unidade_educacional"):
            kwargs["escola__tipo_unidade__uuid"] = query_params.get(
                "unidade_educacional"
            )
        if query_params.get("data_inicial"):
            kwargs["formulario_base__data__gte"] = query_params.get("data_inicial")
        if query_params.get("data_final"):
            kwargs["formulario_base__data__lte"] = query_params.get("data_final")
        return kwargs

    def get_lista_status(self) -> list[str]:
        lista_status = [
            state.name for state in list(FormularioSupervisaoWorkflow.states)
        ]
        lista_status += ["TODOS_OS_LANCAMENTOS"]
        return lista_status

    def get_label(self, workflow: str) -> str:
        try:
            return FormularioSupervisaoWorkflow.states[workflow].title
        except KeyError:
            return "Todos os Lançamentos"

    def dados_dashboard(self, query_set: QuerySet, kwargs: dict) -> list:
        sumario = []

        for workflow in self.get_lista_status():
            todos_lancamentos = workflow == "TODOS_OS_LANCAMENTOS"
            qs = (
                query_set.filter(status=workflow)
                if not todos_lancamentos
                else query_set
            )
            qs = qs.filter(**kwargs)
            sumario.append(
                {
                    "status": workflow,
                    "label": self.get_label(workflow),
                    "total": len(qs),
                }
            )
        return sumario

    @action(
        detail=False,
        methods=["GET"],
        url_path="dashboard",
        permission_classes=[UsuarioCODAENutriSupervisao],
    )
    def dashboard(self, request):
        query_set = self.get_queryset()
        kwargs = self.formatar_filtros(request.query_params)
        response = {
            "results": self.dados_dashboard(
                query_set=query_set,
                kwargs=kwargs,
            )
        }
        return Response(response)


class FormularioDiretorModelViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = FormularioSupervisao.objects.all().order_by("-criado_em")
    permission_classes = (UsuarioEscolaTercTotal,)
    serializer_class = FormularioSupervisaoSerializer
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        return {
            "list": FormularioSupervisaoSerializer,
            "retrieve": FormularioSupervisaoSerializer,
        }.get(self.action, FormularioDiretorManyCreateSerializer)

    @action(
        detail=False,
        url_path="tipos-ocorrencias",
    )
    def tipos_ocorrencias(self, request):
        edital_uuid = request.query_params.get("edital_uuid")

        try:
            edital = Edital.objects.get(uuid=edital_uuid)
        except Edital.DoesNotExist:
            return Response(
                {
                    "detail": "Edital do tipo IMR com o UUID informado não foi encontrado."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        queryset = TipoOcorrencia.para_diretores.filter(edital=edital)

        serializer = TipoOcorrenciaSerializer(queryset, many=True)

        return Response(serializer.data)


class UtensilioCozinhaViewSet(viewsets.ModelViewSet):
    queryset = UtensilioCozinha.objects.all()
    serializer_class = UtensilioCozinhaSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"

    def list(self, request, *args, **kwargs):
        self.queryset = UtensilioCozinha.ativos.all()

        edital_uuid = request.query_params.get("edital_uuid")

        if edital_uuid:
            self.queryset = self.queryset.filter(
                editalutensiliocozinha__edital__uuid=edital_uuid
            ).distinct("nome")

        serializer = self.get_serializer(self.queryset, many=True)
        return Response({"results": serializer.data})


class UtensilioMesaViewSet(viewsets.ModelViewSet):
    queryset = UtensilioMesa.objects.all()
    serializer_class = UtensilioMesaSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"

    def list(self, request, *args, **kwargs):
        self.queryset = UtensilioMesa.ativos.all()

        edital_uuid = request.query_params.get("edital_uuid")

        if edital_uuid:
            self.queryset = self.queryset.filter(
                editalutensiliomesa__edital__uuid=edital_uuid
            ).distinct("nome")

        serializer = self.get_serializer(self.queryset, many=True)
        return Response({"results": serializer.data})


class EquipamentoViewSet(viewsets.ModelViewSet):
    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"

    def list(self, request, *args, **kwargs):
        self.queryset = Equipamento.ativos.all()

        edital_uuid = request.query_params.get("edital_uuid")

        if edital_uuid:
            self.queryset = self.queryset.filter(
                editalequipamento__edital__uuid=edital_uuid
            ).distinct("nome")

        serializer = self.get_serializer(self.queryset, many=True)
        return Response({"results": serializer.data})


class MobiliarioViewSet(viewsets.ModelViewSet):
    queryset = Mobiliario.objects.all()
    serializer_class = MobiliarioSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"

    def list(self, request, *args, **kwargs):
        self.queryset = Mobiliario.ativos.all()

        edital_uuid = request.query_params.get("edital_uuid")

        if edital_uuid:
            self.queryset = self.queryset.filter(
                editalmobiliario__edital__uuid=edital_uuid
            ).distinct("nome")

        serializer = self.get_serializer(self.queryset, many=True)
        return Response({"results": serializer.data})


class ReparoEAdaptacaoViewSet(viewsets.ModelViewSet):
    queryset = ReparoEAdaptacao.objects.all()
    serializer_class = ReparoEAdaptacaoSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"

    def list(self, request, *args, **kwargs):
        self.queryset = ReparoEAdaptacao.ativos.all()

        edital_uuid = request.query_params.get("edital_uuid")

        if edital_uuid:
            self.queryset = self.queryset.filter(
                editalreparoeadaptacao__edital__uuid=edital_uuid
            ).distinct("nome")

        serializer = self.get_serializer(self.queryset, many=True)
        return Response({"results": serializer.data})


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"

    def list(self, request, *args, **kwargs):
        self.queryset = Insumo.ativos.all()

        edital_uuid = request.query_params.get("edital_uuid")

        if edital_uuid:
            self.queryset = self.queryset.filter(
                editalinsumo__edital__uuid=edital_uuid
            ).distinct("nome")

        serializer = self.get_serializer(self.queryset, many=True)
        return Response({"results": serializer.data})
