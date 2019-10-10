from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from xworkflows import InvalidTransitionError

from .permissions import (
    PodeAprovarPelaCODAEAlteracaoCardapioPermission, PodeIniciarAlteracaoCardapioPermission,
    PodeIniciarSuspensaoDeAlimentacaoPermission, PodeRecusarPelaCODAEAlteracaoCardapioPermission,
    PodeTomarCienciaSuspensaoDeAlimentacaoPermission
)
from .serializers.serializers import (
    AlteracaoCardapioSerializer, AlteracaoCardapioSimplesSerializer,
    CardapioSerializer, GrupoSupensaoAlimentacaoListagemSimplesSerializer,
    GrupoSuspensaoAlimentacaoSerializer, GrupoSuspensaoAlimentacaoSimplesSerializer,
    InversaoCardapioSerializer, MotivoAlteracaoCardapioSerializer,
    MotivoSuspensaoSerializer, TipoAlimentacaoSerializer
)
from .serializers.serializers_create import (
    AlteracaoCardapioSerializerCreate, CardapioCreateSerializer,
    GrupoSuspensaoAlimentacaoCreateSerializer, InversaoCardapioSerializerCreate)
from ..models import (AlteracaoCardapio, Cardapio, GrupoSuspensaoAlimentacao, InversaoCardapio, MotivoAlteracaoCardapio,
                      MotivoSuspensao, TipoAlimentacao)
from ...dados_comuns import constants


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
            url_path=f'{constants.PEDIDOS_DRE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_diretoria_regional(self, request, filtro_aplicado=constants.SEM_FILTRO):
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
            url_path=f'{constants.PEDIDOS_CODAE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_codae(self, request, filtro_aplicado=constants.SEM_FILTRO):
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
            url_path=f'{constants.PEDIDOS_TERCEIRIZADA}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_terceirizada(self, request, filtro_aplicado=constants.SEM_FILTRO):
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

    @action(detail=False, url_path='pedidos-reprovados-diretoria-regional')
    def pedidos_reprovados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inversoes_cardapio = diretoria_regional.inversoes_cardapio_reprovados
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

    @action(detail=False, url_path='pedidos-reprovados-codae')
    def pedidos_reprovados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inversoes_cardapio = codae.inversoes_cardapio_reprovados
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

    @action(detail=False, url_path=constants.SOLICITACOES_DO_USUARIO)
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
            methods=['patch'], url_path=constants.ESCOLA_INICIO_PEDIDO)
    def inicio_de_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.inicia_fluxo(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.DRE_VALIDA_PEDIDO)
    def diretoria_regional_aprova_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.dre_valida(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.DRE_PEDE_REVISAO)
    def diretoria_regional_pede_revisao(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.dre_pede_revisao(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.DRE_NAO_VALIDA_PEDIDO)
    def diretoria_regional_cancela_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            inversao_cardapio.dre_nao_valida(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.ESCOLA_REVISA_PEDIDO)
    def escola_revisa_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.escola_revisa(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.CODAE_AUTORIZA_PEDIDO)
    def codae_aprova_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.codae_autoriza(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.CODAE_NEGA_PEDIDO)
    def codae_cancela_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            inversao_cardapio.codae_nega(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.TERCEIRIZADA_TOMOU_CIENCIA)
    def terceirizada_toma_ciencia(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.terceirizada_toma_ciencia(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.ESCOLA_CANCELA)
    def escola_cancela_pedido(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.cancelar_pedido(user=request.user, )
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
            url_path=f'{constants.PEDIDOS_CODAE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_codae(self, request, filtro_aplicado=constants.SEM_FILTRO):
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

    @action(detail=False, methods=['GET'],
            url_path=f'{constants.PEDIDOS_TERCEIRIZADA}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        # TODO: colocar regras de Terceirizada aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber
        terceirizada = usuario.terceirizadas.first()
        suspensoes_cardapio = terceirizada.suspensoes_cardapio_das_minhas_escolas(
            filtro_aplicado
        )

        page = self.paginate_queryset(suspensoes_cardapio)
        serializer = GrupoSupensaoAlimentacaoListagemSimplesSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

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
            methods=['patch'], url_path=constants.ESCOLA_INFORMA_SUSPENSAO)
    def informa_suspensao(self, request, uuid=None):
        grupo_suspensao_de_alimentacao = self.get_object()
        try:
            grupo_suspensao_de_alimentacao.informa(user=request.user, )
            serializer = self.get_serializer(grupo_suspensao_de_alimentacao)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeTomarCienciaSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.TERCEIRIZADA_TOMOU_CIENCIA)
    def terceirizada_toma_ciencia(self, request, uuid=None):
        grupo_suspensao_de_alimentacao = self.get_object()
        try:
            grupo_suspensao_de_alimentacao.terceirizada_toma_ciencia(user=request.user, )
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
            url_path=f'{constants.PEDIDOS_CODAE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_codae(self, request, filtro_aplicado=constants.SEM_FILTRO):
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

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_DRE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_dre(self, request, filtro_aplicado=constants.SEM_FILTRO):
        # TODO: colocar regras de DRE aqui...
        usuario = request.user
        dre = usuario.diretorias_regionais.first()
        alteracoes_cardapio = dre.alteracoes_cardapio_das_minhas_escolas_a_validar(
            filtro_aplicado
        )

        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = AlteracaoCardapioSimplesSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_TERCEIRIZADA}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_terceirizada(self, request, filtro_aplicado=constants.SEM_FILTRO):
        # TODO: colocar regras de Terceirizada aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber
        terceirizada = usuario.terceirizadas.first()
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_das_minhas(
            filtro_aplicado
        )

        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = AlteracaoCardapioSimplesSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    #
    # IMPLEMENTAÇÃO DO FLUXO (PARTINDO DA ESCOLA)
    #

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.ESCOLA_INICIO_PEDIDO)
    def inicio_de_pedido(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.inicia_fluxo(user=request.user, )
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.DRE_VALIDA_PEDIDO)
    def diretoria_regional_aprova(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.dre_valida(user=request.user, )
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.DRE_PEDE_REVISAO)
    def dre_pede_revisao(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.dre_pede_revisao(user=request.user)
            serializer = self.get_serializer(alteracao_cardapio, )
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.DRE_NAO_VALIDA_PEDIDO)
    def dre_cancela_pedido(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            alteracao_cardapio.dre_nao_valida(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.ESCOLA_REVISA_PEDIDO)
    def escola_revisa(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.escola_revisa(user=request.user, )
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.CODAE_NEGA_PEDIDO)
    def codae_cancela_pedido(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            alteracao_cardapio.codae_nega(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeAprovarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.CODAE_AUTORIZA_PEDIDO)
    def codae_aprova(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.codae_autoriza(user=request.user, )
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.TERCEIRIZADA_TOMOU_CIENCIA)
    def terceirizada_toma_ciencia(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.terceirizada_toma_ciencia(user=request.user, )
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.ESCOLA_CANCELA)
    def escola_cancela_pedido(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()

        try:
            inclusao_alimentacao_continua.cancelar_pedido(user=request.user, )
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

    @action(detail=False, url_path='pedidos-autorizados-diretoria-regional')
    def pedidos_autorizados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_autorizadas
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

    @action(detail=False, url_path='pedidos-autorizados-codae')
    def pedidos_autorizados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        alteracoes_cardapio = codae.alteracoes_cardapio_autorizadas
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

    @action(detail=False, url_path='pedidos-autorizados-terceirizada')
    def pedidos_autorizados_terceirizada(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_autorizadas
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

    # TODO rever os demais endpoints. Essa action consolida em uma única pesquisa as pesquisas por prioridade.
    @action(detail=False,
            url_path=f'{constants.PEDIDOS_DRE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_das_minhas_escolas_a_validar(
            filtro_aplicado
        )
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
