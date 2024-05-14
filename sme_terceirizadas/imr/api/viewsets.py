from django.core.exceptions import ValidationError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sme_terceirizadas.dados_comuns.api.paginations import DefaultPagination
from sme_terceirizadas.dados_comuns.permissions import UsuarioCODAENutriSupervisao
from sme_terceirizadas.terceirizada.models import Edital

from ..models import FormularioSupervisao, PeriodoVisita, TipoOcorrencia
from .serializers.serializers import (
    FormularioSupervisaoSerializer,
    PeriodoVisitaSerializer,
    TipoOcorrenciaSerializer,
)
from .serializers.serializers_create import FormularioSupervisaoRascunhoCreateSerializer


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
        }.get(self.action, FormularioSupervisaoRascunhoCreateSerializer)

    @action(detail=False, url_path="tipos-ocorrencias")
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
