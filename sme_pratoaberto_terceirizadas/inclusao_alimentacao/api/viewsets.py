from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import MotivoInclusaoContinua, InclusaoAlimentacaoNormal, \
    GrupoInclusaoAlimentacaoNormal, MotivoInclusaoNormal
from .serializers import serializers, serializers_create


class MotivoInclusaoContinuaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoInclusaoContinua.objects.all()
    serializer_class = serializers.MotivoInclusaoContinuaSerializer


class MotivoInclusaoNormalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoInclusaoNormal.objects.all()
    serializer_class = serializers.MotivoInclusaoNormalSerializer


class InclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = InclusaoAlimentacaoNormal.objects.all()
    serializer_class = serializers.InclusaoAlimentacaoNormalSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.InclusaoAlimentacaoNormalCreationSerializer
        return serializers.InclusaoAlimentacaoNormalSerializer


class GrupoInclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = GrupoInclusaoAlimentacaoNormal.objects.all()
    serializer_class = serializers.GrupoInclusaoAlimentacaoNormalSerializer
