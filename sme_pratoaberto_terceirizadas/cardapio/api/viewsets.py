from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response

from xworkflows import InvalidTransitionError

from .permissions import PodeIniciarInversaoDeDiaDeCardapioPermission
from .serializers.serializers import (
    CardapioSerializer, TipoAlimentacaoSerializer,
    InversaoCardapioSerializer, SuspensaoAlimentacaoSerializer, AlteracaoCardapioSerializer
)
from .serializers.serializers import MotivoAlteracaoCardapioSerializer

from .serializers.serializers_create import (
    InversaoCardapioSerializerCreate, CardapioCreateSerializer,
    SuspensaoAlimentacaoCreateSerializer, AlteracaoCardapioSerializerCreate
)

from ..models import Cardapio, TipoAlimentacao, InversaoCardapio, AlteracaoCardapio
from ..models import SuspensaoAlimentacao
from ..models import MotivoAlteracaoCardapio

from .permissions import (
    PodeIniciarAlteracaoCardapioPermission,
    PodeAprovarAlteracaoCardapioPermission
)


class CardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = CardapioSerializer
    queryset = Cardapio.objects.all().order_by('data')

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CardapioCreateSerializer
        return CardapioSerializer


class TipoAlimentacaoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = TipoAlimentacaoSerializer
    queryset = TipoAlimentacao.objects.all()


class InversaoCardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = InversaoCardapioSerializer
    queryset = InversaoCardapio.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InversaoCardapioSerializerCreate
        return InversaoCardapioSerializer

    @action(detail=False, url_path="minhas-solicitacoes")
    def minhas_solicitacoes(self, request):
        usuario = request.user
        solicitacoes_unificadas = InversaoCardapio.objects.filter(
            criado_por=usuario,
            status=InversaoCardapio.workflow_class.RASCUNHO
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[PodeIniciarInversaoDeDiaDeCardapioPermission])
    def inicio_de_pedido(self, request, uuid=None):
        inversao_dia_cardapio = self.get_object()
        try:
            inversao_dia_cardapio.inicia_fluxo(user=request.user)
            serializer = self.get_serializer(inversao_dia_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    def destroy(self, request, *args, **kwargs):
        inversao_dia_cardapio = self.get_object()
        if inversao_dia_cardapio.pode_excluir:
            return super().destroy(request, *args, **kwargs)


class SuspensaoAlimentacaoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = SuspensaoAlimentacao.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SuspensaoAlimentacaoCreateSerializer
        return SuspensaoAlimentacaoSerializer


class AlteracoesCardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = AlteracaoCardapio.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AlteracaoCardapioSerializerCreate
        return AlteracaoCardapioSerializer

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission], methods=['patch'])
    def inicio_de_pedido(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.inicia_fluxo(user=request.user)
            serializer = self.get_serializer(alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))


class MotivosAlteracaoCardapioViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoAlteracaoCardapio.objects.all()
    serializer_class = MotivoAlteracaoCardapioSerializer


class AlteracoesCardapioRascunhoViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = AlteracaoCardapio.objects.filter(status="RASCUNHO")
    serializer_class = AlteracaoCardapioSerializer
