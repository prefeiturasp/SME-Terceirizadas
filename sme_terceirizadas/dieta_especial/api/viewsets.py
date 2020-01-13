from rest_framework import mixins, status

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..models import AlergiaIntolerancia, ClassificacaoDieta, MotivoNegacao, SolicitacaoDietaEspecial, TipoDieta
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

    @action(detail=True, methods=['post'])
    def autoriza(self, request, uuid=None):
        return Response("Eba! Vais autorizar!1!")

    @action(detail=True, methods=['post'])
    def negar(self, request, uuid=None):
        solicitacao = self.get_object()
        solicitacao.justificativa_negacao = request.data['justificativa']
        solicitacao.motivo_negacao_id = request.data['motivo']
        solicitacao.codae_nega(user=request.user)
        solicitacao.save()
        return Response({"mensagem": "Solicitação de Dieta Especial Negada"})


class AlergiaIntoleranciaViewSet(mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 GenericViewSet):
    queryset = AlergiaIntolerancia.objects.all()
    serializer_class = AlergiaIntoleranciaSerializer
    pagination_class = None


class ClassificacaoDietaViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                GenericViewSet):
    queryset = ClassificacaoDieta.objects.all()
    serializer_class = ClassificacaoDietaSerializer
    pagination_class = None


class MotivoNegacaoViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           GenericViewSet):
    queryset = MotivoNegacao.objects.all()
    serializer_class = MotivoNegacaoSerializer
    pagination_class = None


class TipoDietaViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       GenericViewSet):
    queryset = TipoDieta.objects.all()
    serializer_class = TipoDietaSerializer
    pagination_class = None
