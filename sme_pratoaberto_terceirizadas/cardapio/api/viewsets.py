from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from xworkflows import InvalidTransitionError

from sme_pratoaberto_terceirizadas.cardapio.api.serializers.serializers import MotivoSuspensaoSerializer
from .permissions import (
    PodeIniciarAlteracaoCardapioPermission,
    PodeAprovarPelaDREAlteracaoCardapioPermission,
    PodePedirRevisaoPelaDREAlteracaoCardapioPermission,
    PodeAprovarPelaCODAEAlteracaoCardapioPermission,
    PodeRecusarPelaCODAEAlteracaoCardapioPermission,
)
from .permissions import PodeIniciarInversaoDeDiaDeCardapioPermission, PodeIniciarSuspensaoDeAlimentacaoPermission
from .serializers.serializers import (
    CardapioSerializer, TipoAlimentacaoSerializer,
    InversaoCardapioSerializer, AlteracaoCardapioSerializer,
    GrupoSuspensaoAlimentacaoSerializer)
from .serializers.serializers import MotivoAlteracaoCardapioSerializer
from .serializers.serializers_create import (
    InversaoCardapioSerializerCreate, CardapioCreateSerializer,
    AlteracaoCardapioSerializerCreate,
    GrupoSuspensaoAlimentacaoCreateSerializer)
from ..models import (
    Cardapio, TipoAlimentacao, InversaoCardapio,
    AlteracaoCardapio, GrupoSuspensaoAlimentacao, MotivoSuspensao
)
from ..models import MotivoAlteracaoCardapio


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


class GrupoSuspensaoAlimentacaoSerializerViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = GrupoSuspensaoAlimentacao.objects.all()
    serializer_class = GrupoSuspensaoAlimentacaoSerializer

    @action(detail=False, methods=['GET'])
    def meus_rascunhos(self, request):
        usuario = request.user
        grupos_suspensao = GrupoSuspensaoAlimentacao.objects.filter(
            criado_por=usuario,
            status=GrupoSuspensaoAlimentacao.workflow_class.RASCUNHO
        )
        page = self.paginate_queryset(grupos_suspensao)
        serializer = GrupoSuspensaoAlimentacaoSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GrupoSuspensaoAlimentacaoCreateSerializer
        return GrupoSuspensaoAlimentacaoSerializer

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission])
    def inicio_de_pedido(self, request, uuid=None):
        suspensao_de_alimentacao = self.get_object()
        try:
            suspensao_de_alimentacao.inicia_fluxo(user=request.user)
            serializer = self.get_serializer(suspensao_de_alimentacao)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))


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

    @action(detail=True, permission_classes=[PodeAprovarPelaDREAlteracaoCardapioPermission], methods=['patch'])
    def dre_aprovou(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.dre_aprovou(user=request.user)
            serializer = self.get_serializer(alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodePedirRevisaoPelaDREAlteracaoCardapioPermission], methods=['patch'])
    def dre_pediu_revisao(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.dre_pediu_revisao(user=request.user)
            serializer = self.get_serializer(alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission], methods=['patch'])
    def escola_revisou(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.escola_revisou(user=request.user)
            serializer = self.get_serializer(alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarPelaCODAEAlteracaoCardapioPermission], methods=['patch'])
    def cadae_aprovou(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.codae_aprovou(user=request.user)
            serializer = self.get_serializer(alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission], methods=['patch'])
    def cadae_recusou(self, request, uuid=None):
        alimentacao_normal = self.get_object()
        try:
            alimentacao_normal.codae_recusou(user=request.user)
            serializer = self.get_serializer(alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=False, methods=['GET'])
    def prazo_vencendo(self, request):
        query_set = AlteracaoCardapio.prazo_vencendo.all()
        page = self.paginate_queryset(query_set)
        serializer = AlteracaoCardapioSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'])
    def prazo_limite(self, request):
        query_set = AlteracaoCardapio.prazo_limite.all()
        page = self.paginate_queryset(query_set)
        serializer = AlteracaoCardapioSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'])
    def prazo_regular(self, request):
        query_set = AlteracaoCardapio.prazo_regular.all()
        page = self.paginate_queryset(query_set)
        serializer = AlteracaoCardapioSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class MotivosAlteracaoCardapioViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoAlteracaoCardapio.objects.all()
    serializer_class = MotivoAlteracaoCardapioSerializer


class AlteracoesCardapioRascunhoViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = AlteracaoCardapio.objects.filter(status="RASCUNHO")
    serializer_class = AlteracaoCardapioSerializer


class MotivosSuspensaoCardapioViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoSuspensao.objects.all()
    serializer_class = MotivoSuspensaoSerializer
