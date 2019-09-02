from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from xworkflows import InvalidTransitionError

from .permissions import (
    PodeIniciarSolicitacaoKitLancheAvulsaPermission, PodeIniciarSolicitacaoUnificadaPermission,
    SolicitacaoUnificadaPermission
)
from .serializers import serializers
from .serializers import serializers_create
from .. import models
from ..models import (
    EscolaQuantidade, SolicitacaoKitLancheAvulsa, SolicitacaoKitLancheUnificada
)
from ...dados_comuns.constants import (
    FILTRO_PADRAO_PEDIDOS, PEDIDOS_CODAE, PEDIDOS_DRE, PEDIDOS_TERCEIRIZADA
)


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
    queryset = SolicitacaoKitLancheAvulsa.objects.all()
    serializer_class = serializers.SolicitacaoKitLancheAvulsaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.SolicitacaoKitLancheAvulsaCreationSerializer
        return serializers.SolicitacaoKitLancheAvulsaSerializer

    @action(detail=False,
            url_path=f"{PEDIDOS_DRE}/{FILTRO_PADRAO_PEDIDOS}")
    def pedidos_diretoria_regional(self, request, filtro_aplicado="sem_filtro"):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        kit_lanches_avulso = diretoria_regional.solicitacoes_kit_lanche_das_minhas_escolas_a_validar(
            filtro_aplicado
        )
        page = self.paginate_queryset(kit_lanches_avulso)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f"{PEDIDOS_CODAE}/{FILTRO_PADRAO_PEDIDOS}")
    def pedidos_codae(self, request, filtro_aplicado="sem_filtro"):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        kit_lanches_avulso = codae.solicitacoes_kit_lanche_das_minhas_escolas_a_validar(
            filtro_aplicado
        )
        page = self.paginate_queryset(kit_lanches_avulso)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f"{PEDIDOS_TERCEIRIZADA}/{FILTRO_PADRAO_PEDIDOS}")
    def pedidos_terceirizadas(self, request, filtro_aplicado="sem_filtro"):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        terceirizadas = usuario.terceirizadas.first()
        kit_lanches_avulso = terceirizadas.solicitacoes_kit_lanche_das_minhas_escolas_a_validar(
            filtro_aplicado
        )
        page = self.paginate_queryset(kit_lanches_avulso)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # TODO: com as permissoes feitas, somente uma pessoa com permissao dentro da escola poder pedir
    @action(detail=False, url_path="minhas-solicitacoes")
    def minhas_solicitacoes(self, request):
        usuario = request.user
        solicitacoes_unificadas = SolicitacaoKitLancheAvulsa.objects.filter(
            criado_por=usuario,
            status=SolicitacaoKitLancheAvulsa.workflow_class.RASCUNHO
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    #
    # IMPLEMENTAÇÃO DO FLUXO (PARTINDO DA ESCOLA)
    #

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="inicio-pedido")
    def inicio_de_pedido(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="diretoria-regional-aprova-pedido")
    def diretoria_regional_aprova_pedido(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.dre_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data, status=HTTP_200_OK)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="diretoria-regional-pede-revisao")
    def diretoria_regional_pede_revisao(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.dre_pediu_revisao(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="diretoria-regional-cancela-pedido")
    def diretoria_regional_cancela_pedido(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.dre_cancelou_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="escola-revisa-pedido")
    def escola_revisa_pedido(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.escola_revisou(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="codae-aprova-pedido")
    def codae_aprova_pedido(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.codae_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="codae-cancela-pedido")
    def codae_cancela_pedido(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.codae_cancelou_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="terceirizada-toma-ciencia")
    def terceirizada_toma_ciencia(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.terceirizada_tomou_ciencia(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSolicitacaoKitLancheAvulsaPermission],
            methods=['patch'], url_path="escola-cancela-pedido-48h-antes")
    def escola_cancela_pedido_48h_antes(self, request, uuid=None):
        solicitacao_kit_lanche_avulsa = self.get_object()
        try:
            solicitacao_kit_lanche_avulsa.cancelar_pedido_48h_antes(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_kit_lanche_avulsa)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        solicitacao_kit_lanche_avulsa = self.get_object()
        if solicitacao_kit_lanche_avulsa.pode_excluir:
            return super().destroy(request, *args, **kwargs)


class SolicitacaoKitLancheUnificadaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoKitLancheUnificada.objects.all()
    serializer_class = serializers.SolicitacaoKitLancheUnificadaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.SolicitacaoKitLancheUnificadaCreationSerializer
        return serializers.SolicitacaoKitLancheUnificadaSerializer

    @action(detail=False,
            url_path=f"{PEDIDOS_CODAE}/{FILTRO_PADRAO_PEDIDOS}")
    def pedidos_codae(self, request, filtro_aplicado="sem_filtro"):
        # TODO: colocar regras de codae CODAE aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        solicitacoes_unificadas = codae.solicitacoes_unificadas(
            filtro_aplicado
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = serializers.SolicitacaoKitLancheUnificadaSimplesSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f"{PEDIDOS_TERCEIRIZADA}/{FILTRO_PADRAO_PEDIDOS}")
    def pedidos_terceirizada(self, request, filtro_aplicado="sem_filtro"):
        # TODO: colocar regras de Terceirizada aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        solicitacoes_unificadas = terceirizada.solicitacoes_unificadas_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False)
    def minhas_solicitacoes(self, request):
        usuario = request.user
        solicitacoes_unificadas = SolicitacaoKitLancheUnificada.get_pedidos_rascunho(usuario)
        page = self.paginate_queryset(solicitacoes_unificadas)
        serializer = serializers.SolicitacaoKitLancheUnificadaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    #
    # IMPLEMENTAÇÃO DO FLUXO (PARTINDO DA DRE)
    #

    @action(detail=True, url_path="inicio-pedido",
            permission_classes=[PodeIniciarSolicitacaoUnificadaPermission], methods=['patch'])
    def inicio_de_pedido(self, request, uuid=None):
        solicitacao_unificada = self.get_object()
        try:
            solicitacoes_unificadas = solicitacao_unificada.dividir_por_lote()
            for solicitacao_unificada in solicitacoes_unificadas:
                solicitacao_unificada.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacoes_unificadas, many=True)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path="codae-aprova-pedido",
            permission_classes=[PodeIniciarSolicitacaoUnificadaPermission], methods=['patch'])
    def codae_aprova(self, request, uuid=None):
        solicitacao_unificada = self.get_object()
        try:
            solicitacao_unificada.codae_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_unificada)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path="codae-pediu-revisao",
            permission_classes=[PodeIniciarSolicitacaoUnificadaPermission], methods=['patch'])
    def codae_pede_revisao(self, request, uuid=None):
        solicitacao_unificada = self.get_object()
        try:
            solicitacao_unificada.codae_pediu_revisao(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_unificada)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path="codae-cancela-pedido",
            permission_classes=[PodeIniciarSolicitacaoUnificadaPermission], methods=['patch'])
    def codae_cancela_pedido(self, request, uuid=None):
        solicitacao_unificada = self.get_object()
        try:
            solicitacao_unificada.codae_cancelou_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_unificada)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path="diretoria-regional-revisa",
            permission_classes=[PodeIniciarSolicitacaoUnificadaPermission], methods=['patch'])
    def dre_revisa(self, request, uuid=None):
        solicitacao_unificada = self.get_object()
        try:
            solicitacao_unificada.dre_revisou(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_unificada)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path="terceirizada-toma-ciencia",
            permission_classes=[PodeIniciarSolicitacaoUnificadaPermission], methods=['patch'])
    def terceirizada_toma_ciencia(self, request, uuid=None):
        solicitacao_unificada = self.get_object()
        try:
            solicitacao_unificada.terceirizada_tomou_ciencia(user=request.user, notificar=True)
            serializer = self.get_serializer(solicitacao_unificada)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        solicitacao_unificada = self.get_object()
        if solicitacao_unificada.pode_excluir:
            return super().destroy(request, *args, **kwargs)


class EscolaQuantidadeViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = EscolaQuantidade.objects.all()
    serializer_class = serializers.EscolaQuantidadeSerializer
    permission_classes = [SolicitacaoUnificadaPermission]

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.EscolaQuantidadeCreationSerializer
        return serializers.EscolaQuantidadeSerializer
