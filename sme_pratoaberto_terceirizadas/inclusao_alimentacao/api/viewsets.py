from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .serializers import serializers, serializers_create
from .. import models


class MotivoInclusaoContinuaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = models.MotivoInclusaoContinua.objects.all()
    serializer_class = serializers.MotivoInclusaoContinuaSerializer


class MotivoInclusaoNormalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = models.MotivoInclusaoNormal.objects.all()
    serializer_class = serializers.MotivoInclusaoNormalSerializer


class InclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.InclusaoAlimentacaoNormal.objects.all()
    serializer_class = serializers.InclusaoAlimentacaoNormalSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.InclusaoAlimentacaoNormalCreationSerializer
        return serializers.InclusaoAlimentacaoNormalSerializer


class GrupoInclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.GrupoInclusaoAlimentacaoNormal.objects.all()
    serializer_class = serializers.GrupoInclusaoAlimentacaoNormalSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.GrupoInclusaoAlimentacaoNormalCreationSerializer
        return serializers.GrupoInclusaoAlimentacaoNormalSerializer


class InclusaoAlimentacaoContinuaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.InclusaoAlimentacaoContinua.objects.all()
    serializer_class = serializers.InclusaoAlimentacaoContinuaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.InclusaoAlimentacaoContinuaCreationSerializer
        return serializers.InclusaoAlimentacaoContinuaSerializer

    # TODO: com as permissoes feitas, somente uma pessoa com permissao dentro da escola poder pedir
    # usar PermissionClasses...
    @action(detail=True, )
    def inicio_de_pedido(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        alimentacao_continua.inicia_fluxo()

    # TODO: com as permissoes feitas, somente uma pessoa com permissao dentro da dre pode confirmar
    # usar PermissionClasses...
    # TODO: fazer uma classe inteligente que busca quem ela tem que notificar
    # entende-se por notificar: mandar emails e usar a lib notify as partes interessadas
    @action(detail=True, )
    def confirma_pedido(self, request, uuid=None):
        alimentacao_continua = self.get_object()
        alimentacao_continua.dre_aprovou()

    def destroy(self, request, *args, **kwargs):
        alimentacao_continua = self.get_object()
        if alimentacao_continua.pode_excluir:
            return super().destroy(request, *args, **kwargs)
