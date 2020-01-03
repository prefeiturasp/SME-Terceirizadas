from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from ..models import (
    AlergiaIntolerancia,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    TipoDieta
)
from .serializers import (
    AlergiaIntoleranciaSerializer,
    ClassificacaoDietaSerializer,
    MotivoNegacaoSerializer,
    SolicitacaoDietaEspecialCreateSerializer,
    SolicitacaoDietaEspecialSerializer,
    TipoDietaSerializer
)


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


class AlergiaIntoleranciaViewSet(mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 GenericViewSet):
    queryset = AlergiaIntolerancia.objects.all()
    serializer_class = AlergiaIntoleranciaSerializer


class ClassificacaoDietaViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                GenericViewSet):
    queryset = ClassificacaoDieta.objects.all()
    serializer_class = ClassificacaoDietaSerializer


class MotivoNegacaoViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           GenericViewSet):
    queryset = MotivoNegacao.objects.all()
    serializer_class = MotivoNegacaoSerializer


class TipoDietaViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       GenericViewSet):
    queryset = TipoDieta.objects.all()
    serializer_class = TipoDietaSerializer
