from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from ..models import SolicitacaoDietaEspecial
from .serializers import SolicitacaoDietaEspecialSerializer


class SolicitacaoDietaEspecialViewSet(mixins.RetrieveModelMixin,
                                      mixins.ListModelMixin,
                                      mixins.CreateModelMixin,
                                      GenericViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoDietaEspecial.objects.all()
    serializer_class = SolicitacaoDietaEspecialSerializer
