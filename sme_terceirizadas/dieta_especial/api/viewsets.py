from rest_framework.viewsets import ReadOnlyModelViewSet

from sme_terceirizadas.dieta_especial.api.serializers import SolicitacaoDietaEspecialSerializer
from sme_terceirizadas.dieta_especial.models import SolicitacaoDietaEspecial


class SolicitacaoDietaEspecialViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoDietaEspecial.objects.all()
    serializer_class = SolicitacaoDietaEspecialSerializer
