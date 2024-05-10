from rest_framework import mixins, viewsets

from sme_terceirizadas.dados_comuns.api.paginations import DefaultPagination
from sme_terceirizadas.dados_comuns.permissions import UsuarioCODAENutriSupervisao

from ..models import FormularioSupervisao, PeriodoVisita
from .serializers.serializers import (
    FormularioSupervisaoSerializer,
    PeriodoVisitaSerializer,
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
