from django.core.exceptions import ValidationError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sme_terceirizadas.dados_comuns.api.paginations import DefaultPagination
from sme_terceirizadas.dados_comuns.permissions import (
    UsuarioCODAENutriSupervisao,
    UsuarioEscolaTercTotal,
)
from sme_terceirizadas.terceirizada.models import Edital

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
from .serializers.serializers import (
    EquipamentoSerializer,
    FormularioSupervisaoSerializer,
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
    FormularioSupervisaoRascunhoCreateSerializer,
    FormularioSupervisaoCreateSerializer
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
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = FormularioSupervisao.objects.all().order_by("-criado_em")
    permission_classes = (UsuarioCODAENutriSupervisao,)
    serializer_class = FormularioSupervisaoSerializer
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        return {
            "list": FormularioSupervisaoSerializer,
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


class UtensilioMesaViewSet(viewsets.ModelViewSet):
    queryset = UtensilioMesa.objects.all()
    serializer_class = UtensilioMesaSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"


class EquipamentoViewSet(viewsets.ModelViewSet):
    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"


class MobiliarioViewSet(viewsets.ModelViewSet):
    queryset = Mobiliario.objects.all()
    serializer_class = MobiliarioSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"


class ReparoEAdaptacaoViewSet(viewsets.ModelViewSet):
    queryset = ReparoEAdaptacao.objects.all()
    serializer_class = ReparoEAdaptacaoSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    http_method_names = ["get"]
    lookup_field = "uuid"
