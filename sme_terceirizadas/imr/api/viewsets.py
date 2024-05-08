from rest_framework import mixins, viewsets

from sme_terceirizadas.dados_comuns.api.paginations import DefaultPagination
from sme_terceirizadas.dados_comuns.permissions import UsuarioCODAENutriSupervisao

from ..models import PeriodoVisita
from .serializers.serializers import PeriodoVisitaSerializer


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
