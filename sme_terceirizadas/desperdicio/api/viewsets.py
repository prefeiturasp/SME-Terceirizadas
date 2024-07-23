from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination

from ...dados_comuns import constants

from ..forms import (
    ControleRestosForm,
    ControleRestosRelatorioForm,
    ControleSobrasForm,
    ControleSobrasRelatorioForm,
)

from .serializers.serializers import (
    ControleSobrasSerializer,
    ControleSobrasCreateSerializer,
    ClassificacaoSerializer,
    ClassificacaoCreateSerializer,
    ControleRestosCreateSerializer,
    ControleRestosSerializer,
    serialize_relatorio_controle_sobras,
    serialize_relatorio_controle_sobras_bruto,
    serialize_relatorio_controle_restos,
)

from ..models import (
    Classificacao,
    ControleSobras,
    ControleRestos
)

from ..tasks import (
    gera_xls_relatorio_controle_sobras_async,
    gera_xls_relatorio_controle_sobras_bruto_async,
    gera_xls_relatorio_controle_restos_async
)

from ..utils import (
    obtem_dados_relatorio_controle_restos,
    obtem_dados_relatorio_controle_sobras,
    paginate_list,
)

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "previous": self.get_previous_link(),
                "next": self.get_next_link(),
                "count": self.page.paginator.count,
                "page_size": int(self.request.GET.get("page_size", self.page_size)),
                "results": data,
            }
        )
    

class ControleSobrasViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    queryset = ControleSobras.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ControleSobrasCreateSerializer
        return ControleSobrasSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if "page" in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data})

    def get_queryset(self):
        form = ControleSobrasForm(self.request.GET)
        if not form.is_valid():
            raise ValidationError(form.errors)

        user = self.request.user

        qs = ControleSobras.objects.all().order_by("-criado_em")

        if user.tipo_usuario == "escola":
            qs = qs.filter(escola=user.vinculo_atual.instituicao)

        elif form.cleaned_data["escola"]:
            qs = qs.filter(escola=form.cleaned_data["escola"])

        elif form.cleaned_data["dre"]:
            qs = qs.filter(escola__diretoria_regional=form.cleaned_data["dre"])

        return qs.distinct()

    @action(detail=False, methods=["GET"], url_path=f"{constants.RELATORIO}")
    def relatorio(self, request):
        try:
            form = ControleSobrasRelatorioForm(self.request.GET)
            if not form.is_valid():
                raise ValidationError(form.errors)

            rows = obtem_dados_relatorio_controle_sobras(
                form.cleaned_data, self.request.user
            )
            data = paginate_list(
                request, rows, serializer=serialize_relatorio_controle_sobras
            )
            return Response(data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=["GET"], url_path=f"{constants.RELATORIO}/exportar-xlsx"
    )
    def relatorio_exportar_xlsx(self, request):
        try:
            form = ControleSobrasRelatorioForm(self.request.GET)
            if not form.is_valid():
                raise ValidationError(form.errors)

            rows = obtem_dados_relatorio_controle_sobras(
                form.cleaned_data, self.request.user
            )
            user = request.user.get_username()
            gera_xls_relatorio_controle_sobras_async.delay(
                user=user,
                nome_arquivo="relatorio_controle_sobras.xlsx",
                data=rows,
            )
            return Response(
                dict(detail="Solicitação de geração de arquivo recebida com sucesso."),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    class Meta:
        model = ControleSobras

    @action(detail=False, methods=["GET"], url_path=f"{constants.RELATORIO}-bruto")
    def relatorio_bruto(self, request):
        try:
            form = ControleSobrasRelatorioForm(self.request.GET)
            if not form.is_valid():
                raise ValidationError(form.errors)

            rows = obtem_dados_relatorio_controle_sobras(
                form.cleaned_data, self.request.user, bruto=True
            )
            data = paginate_list(
                request, rows, serializer=serialize_relatorio_controle_sobras_bruto
            )
            return Response(data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=["GET"], url_path=f"{constants.RELATORIO}-bruto/exportar-xlsx"
    )
    def relatorio_bruto_exportar_xlsx(self, request):
        try:
            form = ControleSobrasRelatorioForm(self.request.GET)
            if not form.is_valid():
                raise ValidationError(form.errors)

            rows = obtem_dados_relatorio_controle_sobras(
                form.cleaned_data, self.request.user, bruto=True
            )
            user = request.user.get_username()
            gera_xls_relatorio_controle_sobras_bruto_async.delay(
                user=user,
                nome_arquivo="relatorio_controle_sobras_bruto.xlsx",
                data=rows,
            )
            return Response(
                dict(detail="Solicitação de geração de arquivo recebida com sucesso."),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    class Meta:
        model = ControleSobras


class ControleRestosViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    queryset = ControleRestos.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ControleRestosCreateSerializer
        return ControleRestosSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if "page" in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data})

    def get_queryset(self):
        form = ControleRestosForm(self.request.GET)
        if not form.is_valid():
            raise ValidationError(form.errors)

        user = self.request.user

        qs = ControleRestos.objects.all().order_by("-criado_em")

        if user.tipo_usuario == "escola":
            qs = qs.filter(escola=user.vinculo_atual.instituicao)

        elif form.cleaned_data["escola"]:
            qs = qs.filter(escola=form.cleaned_data["escola"])

        elif form.cleaned_data["dre"]:
            qs = qs.filter(escola__diretoria_regional=form.cleaned_data["dre"])

        return qs.distinct()

    @action(detail=False, methods=["GET"], url_path=f"{constants.RELATORIO}")
    def relatorio(self, request):
        try:
            form = ControleRestosRelatorioForm(self.request.GET)
            if not form.is_valid():
                raise ValidationError(form.errors)

            rows = obtem_dados_relatorio_controle_restos(
                form.cleaned_data, self.request.user
            )
            data = paginate_list(
                request, rows, serializer=serialize_relatorio_controle_restos
            )
            return Response(data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=["GET"], url_path=f"{constants.RELATORIO}/exportar-xlsx"
    )
    def relatorio_exportar_xlsx(self, request):
        try:
            form = ControleRestosRelatorioForm(self.request.GET)
            if not form.is_valid():
                raise ValidationError(form.errors)

            rows = obtem_dados_relatorio_controle_restos(
                form.cleaned_data, self.request.user
            )
            user = request.user.get_username()
            gera_xls_relatorio_controle_restos_async.delay(
                user=user,
                nome_arquivo="relatorio_controle_restos.xlsx",
                data=rows,
            )
            return Response(
                dict(detail="Solicitação de geração de arquivo recebida com sucesso."),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    class Meta:
        model = ControleRestos

class ClassificacaoViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    queryset = Classificacao.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ClassificacaoCreateSerializer
        return ClassificacaoSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data})

    def get_queryset(self):
        qs = Classificacao.objects.all().order_by("tipo", "valor")        

        return qs.distinct()