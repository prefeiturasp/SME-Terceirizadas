from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .permissions import SolicitacaoUnificadaPermission
from .serializers import serializers
from .serializers import serializers_create
from .. import models


class MotivoSolicitacaoUnificadaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.MotivoSolicitacaoUnificada.objects.all()
    serializer_class = serializers.MotivoSolicitacaoUnificadaSerializer


class KitLancheViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = models.KitLanche.objects.all()
    serializer_class = serializers.KitLancheSerializer


class SolicitacaoKitLancheAvulsaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.SolicitacaoKitLancheAvulsa.objects.all()
    serializer_class = serializers.SolicitacaoKitLancheAvulsaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.SolicitacaoKitLancheAvulsaCreationSerializer
        return serializers.SolicitacaoKitLancheAvulsaSerializer

    # TODO: com as permissoes feitas, somente uma pessoa com permissao dentro da escola poder pedir
    # usar PermissionClasses...
    @action(detail=True, )
    def inicio_de_pedido(self, request, uuid=None):
        solicitacao = self.get_object()
        solicitacao.inicia_fluxo()

    def destroy(self, request, *args, **kwargs):
        solicitacao = self.get_object()
        if solicitacao.pode_excluir:
            return super().destroy(request, *args, **kwargs)


class SolicitacaoKitLancheUnificadaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.SolicitacaoKitLancheUnificada.objects.all()
    serializer_class = serializers.SolicitacaoKitLancheUnificadaSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    # TODO: permitir atualizar (update) os EscolaQuantidade alinhados.
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.SolicitacaoKitLancheUnificadaCreationSerializer
        return serializers.SolicitacaoKitLancheUnificadaSerializer


class EscolaQuantidadeViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = models.EscolaQuantidade.objects.all()
    serializer_class = serializers.EscolaQuantidadeSerializer
    permission_classes = [SolicitacaoUnificadaPermission]

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.EscolaQuantidadeCreationSerializer
        return serializers.EscolaQuantidadeSerializer
