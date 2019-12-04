from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from ..models import SolicitacaoDietaEspecial
from .serializers import SolicitacaoDietaEspecialCreateSerializer, SolicitacaoDietaEspecialSerializer


class SolicitacaoDietaEspecialViewSet(mixins.RetrieveModelMixin,
                                      mixins.ListModelMixin,
                                      mixins.CreateModelMixin,
                                      GenericViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoDietaEspecial.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitacaoDietaEspecialCreateSerializer
        return SolicitacaoDietaEspecialSerializer
