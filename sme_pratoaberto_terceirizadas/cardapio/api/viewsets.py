from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from xworkflows import InvalidTransitionError

from .permissions import (
    PodeAprovarPelaCODAEAlteracaoCardapioPermission, PodeIniciarAlteracaoCardapioPermission,
    PodeRecusarPelaCODAEAlteracaoCardapioPermission
)
from .permissions import (
    PodeIniciarSuspensaoDeAlimentacaoPermission,
    PodeTomarCienciaSuspensaoDeAlimentacaoPermission
)
from .serializers.serializers import (
    AlteracaoCardapioSerializer, AlteracaoCardapioSimplesSerializer, CardapioSerializer,
    GrupoSupensaoAlimentacaoListagemSimplesSerializer,
    GrupoSuspensaoAlimentacaoSerializer, InversaoCardapioSerializer,
    TipoAlimentacaoSerializer)
from .serializers.serializers import (
    MotivoAlteracaoCardapioSerializer,
    MotivoSuspensaoSerializer
)
from .serializers.serializers_create import (
    AlteracaoCardapioSerializerCreate, CardapioCreateSerializer,
    GrupoSuspensaoAlimentacaoCreateSerializer, InversaoCardapioSerializerCreate)
from ..api.serializers.serializers import GrupoSuspensaoAlimentacaoSimplesSerializer
from ..models import (
    AlteracaoCardapio, Cardapio, GrupoSuspensaoAlimentacao, InversaoCardapio, TipoAlimentacao
)
from ...cardapio.models import MotivoAlteracaoCardapio, MotivoSuspensao
from ...dados_comuns.constants import (
    FILTRO_PADRAO_PEDIDOS, PEDIDOS_CODAE, PEDIDOS_DRE, PEDIDOS_TERCEIRIZADA, SOLICITACOES_DO_USUARIO
)
from ...dados_comuns.constants import SEM_FILTRO


class CardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = CardapioSerializer
    queryset = Cardapio.objects.all().order_by('data')

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

    @action(detail=False,
            url_path=f'{PEDIDOS_DRE}/{FILTRO_PADRAO_PEDIDOS}')
    def pedidos_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inversoes_cardapio = diretoria_regional.inversoes_cardapio_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{PEDIDOS_CODAE}/{FILTRO_PADRAO_PEDIDOS}')
    def pedidos_codae(self, request, filtro_aplicado='sem_filtro'):
        # TODO: colocar regras de codae CODAE aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inversoes_cardapio = codae.inversoes_cardapio_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{PEDIDOS_TERCEIRIZADA}/{FILTRO_PADRAO_PEDIDOS}')
    def pedidos_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        # TODO: colocar regras de Terceirizada aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inversoes_cardapio = terceirizada.inversoes_cardapio_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-diretoria-regional')
    def pedidos_aprovados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inversoes_cardapio = diretoria_regional.inversoes_cardapio_aprovadas
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-codae')
    def pedidos_aprovados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inversoes_cardapio = codae.inversoes_cardapio_aprovadas
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-terceirizada')
    def pedidos_aprovados_terceirizada(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual TERCEIRIZADA eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inversoes_cardapio = terceirizada.inversoes_cardapio_aprovadas
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InversaoCardapioSerializerCreate
        return InversaoCardapioSerializer

    @action(detail=False, url_path=SOLICITACOES_DO_USUARIO)
    def minhas_solicitacoes(self, request):
        usuario = request.user
        inversoes_rascunho = InversaoCardapio.get_solicitacoes_rascunho(usuario)
        page = self.paginate_queryset(inversoes_rascunho)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    #
    # IMPLEMENTAÇÃO DO FLUXO (PARTINDO DA ESCOLA)
    #

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='inicio-pedido')
    def inicio_de_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='diretoria-regional-aprova-pedido')
    def diretoria_regional_aprova_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.dre_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='diretoria-regional-pede-revisao')
    def diretoria_regional_pede_revisao(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.dre_pediu_revisao(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='diretoria-regional-cancela-pedido')
    def diretoria_regional_cancela_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.dre_cancelou_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='escola-revisa-pedido')
    def escola_revisa_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.escola_revisou(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='codae-aprova-pedido')
    def codae_aprova_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.codae_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='codae-cancela-pedido')
    def codae_cancela_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.codae_cancelou_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='terceirizada-toma-ciencia')
    def terceirizada_toma_ciencia(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.terceirizada_tomou_ciencia(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='escola-cancela-pedido-48h-antes')
    def escola_cancela_pedido_48h_antes(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.cancelar_pedido_48h_antes(user=request.user, notificar=True)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        inversao_cardapio = self.get_object()
        if inversao_cardapio.pode_excluir:
            return super().destroy(request, *args, **kwargs)


class GrupoSuspensaoAlimentacaoSerializerViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = GrupoSuspensaoAlimentacao.objects.all()
    serializer_class = GrupoSuspensaoAlimentacaoSerializer

    @action(detail=False,
            url_path=f'{PEDIDOS_CODAE}/{FILTRO_PADRAO_PEDIDOS}')
    def pedidos_codae(self, request, filtro_aplicado=SEM_FILTRO):
        # TODO: colocar regras de codae CODAE aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber
        codae = usuario.CODAE.first()
        alteracoes_cardapio = codae.suspensoes_cardapio_das_minhas_escolas(
            filtro_aplicado
        )

        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = GrupoSuspensaoAlimentacaoSimplesSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'])
    def informadas(self, request):
        grupo_informados = GrupoSuspensaoAlimentacao.get_informados().order_by('-id')
        serializer = GrupoSupensaoAlimentacaoListagemSimplesSerializer(grupo_informados, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path='tomados-ciencia', methods=['GET'])
    def tomados_ciencia(self, request):
        grupo_informados = GrupoSuspensaoAlimentacao.get_tomados_ciencia()
        page = self.paginate_queryset(grupo_informados)
        serializer = GrupoSuspensaoAlimentacaoSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'])
    def meus_rascunhos(self, request):
        usuario = request.user
        grupos_suspensao = GrupoSuspensaoAlimentacao.get_rascunhos_do_usuario(usuario)
        page = self.paginate_queryset(grupos_suspensao)
        serializer = GrupoSuspensaoAlimentacaoSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GrupoSuspensaoAlimentacaoCreateSerializer
        return GrupoSuspensaoAlimentacaoSerializer

    #
    # IMPLEMENTAÇÃO DO FLUXO (INFORMATIVO PARTINDO DA ESCOLA)
    #

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='informa-suspensao')
    def informa_suspensao(self, request, uuid=None):
        grupo_suspensao_de_alimentacao = self.get_object()
        try:
            grupo_suspensao_de_alimentacao.informa(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_suspensao_de_alimentacao)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeTomarCienciaSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path='terceirizada-toma-ciencia')
    def terceirizada_tomou_ciencia(self, request, uuid=None):
        grupo_suspensao_de_alimentacao = self.get_object()
        try:
            grupo_suspensao_de_alimentacao.terceirizada_tomou_ciencia(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_suspensao_de_alimentacao)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        grupo_suspensao_de_alimentacao = self.get_object()
        if grupo_suspensao_de_alimentacao.pode_excluir:
            return super().destroy(request, *args, **kwargs)


class AlteracoesCardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = AlteracaoCardapio.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AlteracaoCardapioSerializerCreate
        return AlteracaoCardapioSerializer

    #
    # Pedidos
    #

    @action(detail=False,
            url_path='pedidos-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_codae(self, request, filtro_aplicado='sem_filtro'):
        # TODO: colocar regras de codae CODAE aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber
        codae = usuario.CODAE.first()
        alteracoes_cardapio = codae.alteracoes_cardapio_das_minhas(
            filtro_aplicado
        )

        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = AlteracaoCardapioSimplesSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    #
    # IMPLEMENTAÇÃO DO FLUXO (PARTINDO DA ESCOLA)
    #

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path='inicio-pedido')
    def inicio_de_pedido(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path='diretoria-regional-aprova')
    def diretoria_regional_aprova(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.dre_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path='diretoria-regional-pede-revisao')
    def dre_pediu_revisao(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.dre_pediu_revisao(user=request.user)
            serializer = self.get_serializer(alteracao_cardapio, notificar=True)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path='diretoria-regional-cancela-pedido')
    def dre_cancela_pedido(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.dre_cancelou_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path='escola-revisa')
    def escola_revisa(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.escola_revisou(user=request.user, notificar=True)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path='codae-cancela-pedido')
    def codae_cancela_pedido(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.codae_cancelou_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeAprovarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path='codae-aprova-pedido')
    def codae_aprova(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.codae_aprovou(user=request.user, notificar=True)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path='terceirizada-toma-ciencia')
    def terceirizada_tomou_ciencia(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.terceirizada_tomou_ciencia(user=request.user, notificar=True)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path='escola-cancela-pedido-48h-antes')
    def escola_cancela_pedido_48h_antes(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()

        try:
            inclusao_alimentacao_continua.cancelar_pedido_48h_antes(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
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

    @action(detail=False, methods=['GET'], url_path='resumo-de-pendencias/(?P<visao>(dia|semana|mes)+)')
    def resumo_pendencias(self, request, visao='dia'):
        try:
            urgente_query_set = AlteracaoCardapio.solicitacoes_vencendo_por_usuario_e_visao(usuario=request.user,
                                                                                            visao=visao)
            limite_query_set = AlteracaoCardapio.solicitacoes_limite_por_usuario_e_visao(usuario=request.user,
                                                                                         visao=visao)
            regular_query_set = AlteracaoCardapio.solicitacoes_regulares_por_usuario_e_visao(usuario=request.user,
                                                                                             visao=visao)

            urgente_quantidade = urgente_query_set.count()
            limite_quantidade = limite_query_set.count()
            regular_quantidade = regular_query_set.count()

            response = {'urgente': urgente_quantidade, 'limite': limite_quantidade, 'regular': regular_quantidade}
            status_code = status.HTTP_200_OK
        except Exception as e:
            response = {'detail': f'Erro ao sumarizar pendências: {e}'}
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return Response(response, status=status_code)

    @action(detail=False, url_path='pedidos-aprovados-diretoria-regional')
    def pedidos_aprovados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_aprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-diretoria-regional')
    def pedidos_reprovados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_reprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        alteracoes_cardapio = codae.alteracoes_cardapio_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        alteracoes_cardapio = codae.alteracoes_cardapio_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        alteracoes_cardapio = codae.alteracoes_cardapio_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-codae')
    def pedidos_aprovados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        alteracoes_cardapio = codae.alteracoes_cardapio_aprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-codae')
    def pedidos_reprovados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        alteracoes_cardapio = codae.alteracoes_cardapio_reprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-terceirizada')
    def pedidos_aprovados_terceirizada(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_aprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-terceirizada')
    def pedidos_reprovados_terceirizada(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_reprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class MotivosAlteracaoCardapioViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoAlteracaoCardapio.objects.all()
    serializer_class = MotivoAlteracaoCardapioSerializer


class AlteracoesCardapioRascunhoViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = AlteracaoCardapio.objects.filter(status='RASCUNHO')
    serializer_class = AlteracaoCardapioSerializer


class MotivosSuspensaoCardapioViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoSuspensao.objects.all()
    serializer_class = MotivoSuspensaoSerializer
