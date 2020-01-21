from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet
from xworkflows import InvalidTransitionError

from sme_terceirizadas.relatorios.relatorios import relatorio_alteracao_cardapio
from ...dados_comuns import constants
from ..models import (
    AlteracaoCardapio,
    Cardapio,
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    GrupoSuspensaoAlimentacao,
    HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar,
    InversaoCardapio,
    MotivoAlteracaoCardapio,
    MotivoSuspensao,
    SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
)
from .permissions import (
    PodeAprovarPelaCODAEAlteracaoCardapioPermission,
    PodeIniciarAlteracaoCardapioPermission,
    PodeIniciarSuspensaoDeAlimentacaoPermission,
    PodeRecusarPelaCODAEAlteracaoCardapioPermission,
    PodeTomarCienciaSuspensaoDeAlimentacaoPermission
)
from .serializers.serializers import (
    AlteracaoCardapioSerializer,
    AlteracaoCardapioSimplesSerializer,
    CardapioSerializer,
    CombosVinculoTipoAlimentoSimplesSerializer,
    GrupoSupensaoAlimentacaoListagemSimplesSerializer,
    GrupoSuspensaoAlimentacaoSerializer,
    GrupoSuspensaoAlimentacaoSimplesSerializer,
    HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarSerializer,
    InversaoCardapioSerializer,
    MotivoAlteracaoCardapioSerializer,
    MotivoSuspensaoSerializer,
    SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializer,
    TipoAlimentacaoSerializer,
    VinculoTipoAlimentoSimplesSerializer
)
from .serializers.serializers_create import (
    AlteracaoCardapioSerializerCreate,
    CardapioCreateSerializer,
    ComboDoVinculoTipoAlimentoSimplesSerializerCreate,
    GrupoSuspensaoAlimentacaoCreateSerializer,
    HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarSerializerCreate,
    InversaoCardapioSerializerCreate,
    SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializerCreate
)


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


class HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarSerializer
    queryset = HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar.objects.all()

    @action(detail=False, url_path='escola/(?P<escola_uuid>[^/.]+)')
    def filtro_por_escola(self, request, escola_uuid=None):
        combos = HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar.objects.filter(
            escola__uuid=escola_uuid
        )
        page = self.paginate_queryset(combos)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarSerializerCreate
        return HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarSerializer


class VinculoTipoAlimentacaoViewSet(mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = VinculoTipoAlimentoSimplesSerializer
    queryset = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.filter(ativo=True)

    @action(detail=False,
            url_path='tipo_unidade_escolar/(?P<tipo_unidade_escolar_uuid>[^/.]+)')
    def filtro_por_periodo_tipo_ue(self, request, tipo_unidade_escolar_uuid=None):
        vinculos = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.filter(
            tipo_unidade_escolar__uuid=tipo_unidade_escolar_uuid, ativo=True)
        page = self.paginate_queryset(vinculos)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class CombosDoVinculoTipoAlimentacaoPeriodoTipoUEViewSet(mixins.RetrieveModelMixin,
                                                         mixins.ListModelMixin,
                                                         mixins.CreateModelMixin,
                                                         mixins.DestroyModelMixin,
                                                         GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = CombosVinculoTipoAlimentoSimplesSerializer
    queryset = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ComboDoVinculoTipoAlimentoSimplesSerializerCreate
        return CombosVinculoTipoAlimentoSimplesSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.pode_excluir():
            return Response(data={'detail': 'Não pode excluir, o combo já tem movimentação no sistema'},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubstituicaoDoCombosDoVinculoTipoAlimentacaoPeriodoTipoUEViewSet(mixins.RetrieveModelMixin,
                                                                       mixins.ListModelMixin,
                                                                       mixins.CreateModelMixin,
                                                                       mixins.DestroyModelMixin,
                                                                       GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializer
    queryset = SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializerCreate
        return SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.pode_excluir():
            return Response(data={'detail': 'Não pode excluir, o combo já tem movimentação no sistema'},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InversaoCardapioViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = InversaoCardapioSerializer
    queryset = InversaoCardapio.objects.all()

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_DRE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_diretoria_regional(self, request, filtro_aplicado=constants.SEM_FILTRO):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
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
        codae = usuario.vinculo_atual.instituicao
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
        terceirizada = usuario.vinculo_atual.instituicao
        inversoes_cardapio = terceirizada.inversoes_cardapio_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-autorizados-diretoria-regional')
    def pedidos_autorizados_diretoria_regional(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        inversoes_cardapio = diretoria_regional.inversoes_cardapio_autorizadas
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-diretoria-regional')
    def pedidos_reprovados_diretoria_regional(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        inversoes_cardapio = diretoria_regional.inversoes_cardapio_reprovados
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-autorizados-codae')
    def pedidos_autorizados_codae(self, request):
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        inversoes_cardapio = codae.inversoes_cardapio_autorizadas
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-codae')
    def pedidos_reprovados_codae(self, request):
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        inversoes_cardapio = codae.inversoes_cardapio_reprovados
        page = self.paginate_queryset(inversoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-autorizados-terceirizada')
    def pedidos_autorizados_terceirizada(self, request):
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        inversoes_cardapio = terceirizada.inversoes_cardapio_autorizadas
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
    def inicio_de_solicitacao(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.inicia_fluxo(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.DRE_VALIDA_PEDIDO)
    def diretoria_regional_valida_solicitacao(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.dre_valida(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.DRE_NAO_VALIDA_PEDIDO)
    def diretoria_regional_nao_valida_solicitacao(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        try:
            inversao_cardapio.dre_nao_valida(user=request.user, )
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.CODAE_AUTORIZA_PEDIDO)
    def codae_autoriza_solicitacao(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            user = request.user
            if inversao_cardapio.status == inversao_cardapio.workflow_class.DRE_VALIDADO:
                inversao_cardapio.codae_autoriza(user=user)
            else:
                inversao_cardapio.codae_autoriza_questionamento(user=user, justificativa=justificativa)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.CODAE_QUESTIONA_PEDIDO)
    def codae_questiona(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            inversao_cardapio.codae_questiona(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.CODAE_NEGA_PEDIDO)
    def codae_nega_solicitacao(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            user = request.user
            if inversao_cardapio.status == inversao_cardapio.workflow_class.DRE_VALIDADO:
                inversao_cardapio.codae_nega(user=user, justificativa=justificativa)
            else:
                inversao_cardapio.codae_nega_questionamento(user=user, justificativa=justificativa)
            serializer = self.get_serializer(inversao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarSuspensaoDeAlimentacaoPermission],
            methods=['patch'], url_path=constants.TERCEIRIZADA_RESPONDE_QUESTIONAMENTO)
    def terceirizada_responde_questionamento(self, request, uuid=None):
        inversao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        resposta_sim_nao = request.data.get('resposta_sim_nao', False)
        try:
            inversao_cardapio.terceirizada_responde_questionamento(user=request.user, justificativa=justificativa,
                                                                   resposta_sim_nao=resposta_sim_nao)
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
    def escola_cancela_solicitacao(self, request, uuid=None):
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
        codae = usuario.vinculo_atual.instituicao
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
        terceirizada = usuario.vinculo_atual.instituicao
        suspensoes_cardapio = terceirizada.suspensoes_alimentacao_das_minhas_escolas(
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
        codae = usuario.vinculo_atual.instituicao
        alteracoes_cardapio = codae.alteracoes_cardapio_das_minhas(
            filtro_aplicado
        )

        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_DRE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_dre(self, request, filtro_aplicado=constants.SEM_FILTRO):
        # TODO: colocar regras de DRE aqui...
        usuario = request.user
        dre = usuario.vinculo_atual.instituicao
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
        terceirizada = usuario.vinculo_atual.instituicao
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_das_minhas(
            filtro_aplicado
        )

        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['GET'],
            url_path=f'{constants.RELATORIO}')
    def relatorio(self, request, uuid=None):
        return relatorio_alteracao_cardapio(request, solicitacao=self.get_object())

    #
    # IMPLEMENTAÇÃO DO FLUXO (PARTINDO DA ESCOLA)
    #

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.ESCOLA_INICIO_PEDIDO)
    def inicio_de_solicitacao(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.inicia_fluxo(user=request.user, )
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.DRE_VALIDA_PEDIDO)
    def diretoria_regional_valida(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        try:
            alteracao_cardapio.dre_valida(user=request.user, )
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeIniciarAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.DRE_NAO_VALIDA_PEDIDO)
    def dre_nao_valida_solicitacao(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            alteracao_cardapio.dre_nao_valida(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.CODAE_NEGA_PEDIDO)
    def codae_nega_solicitacao(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            if alteracao_cardapio.status == alteracao_cardapio.workflow_class.DRE_VALIDADO:
                alteracao_cardapio.codae_nega(user=request.user, justificativa=justificativa)
            else:
                alteracao_cardapio.codae_nega_questionamento(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeAprovarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.CODAE_AUTORIZA_PEDIDO)
    def codae_autoriza(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            if alteracao_cardapio.status == alteracao_cardapio.workflow_class.DRE_VALIDADO:
                alteracao_cardapio.codae_autoriza(user=request.user)
            else:
                alteracao_cardapio.codae_autoriza_questionamento(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeAprovarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.CODAE_QUESTIONA_PEDIDO)
    def codae_questiona_pedido(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        observacao_questionamento_codae = request.data.get('observacao_questionamento_codae', '')
        try:
            alteracao_cardapio.codae_questiona(
                user=request.user,
                justificativa=observacao_questionamento_codae
            )
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
            methods=['patch'], url_path=constants.TERCEIRIZADA_RESPONDE_QUESTIONAMENTO)
    def terceirizada_responde_questionamento(self, request, uuid=None):
        alteracao_cardapio = self.get_object()
        justificativa = request.data.get('justificativa', '')
        resposta_sim_nao = request.data.get('resposta_sim_nao', False)
        try:
            alteracao_cardapio.terceirizada_responde_questionamento(user=request.user,
                                                                    justificativa=justificativa,
                                                                    resposta_sim_nao=resposta_sim_nao)
            serializer = self.get_serializer(alteracao_cardapio)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[PodeRecusarPelaCODAEAlteracaoCardapioPermission],
            methods=['patch'], url_path=constants.ESCOLA_CANCELA)
    def escola_cancela_solicitacao(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()

        try:
            inclusao_alimentacao_continua.cancelar_pedido(user=request.user, )
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=False, url_path='pedidos-autorizados-diretoria-regional')
    def pedidos_autorizados_diretoria_regional(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_autorizadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-diretoria-regional')
    def pedidos_reprovados_diretoria_regional(self, request):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
        alteracoes_cardapio = diretoria_regional.alteracoes_cardapio_reprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-autorizados-codae')
    def pedidos_autorizados_codae(self, request):
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        alteracoes_cardapio = codae.alteracoes_cardapio_autorizadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-codae')
    def pedidos_reprovados_codae(self, request):
        usuario = request.user
        codae = usuario.vinculo_atual.instituicao
        alteracoes_cardapio = codae.alteracoes_cardapio_reprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-autorizados-terceirizada')
    def pedidos_autorizados_terceirizada(self, request):
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_autorizadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-terceirizada')
    def pedidos_reprovados_terceirizada(self, request):
        usuario = request.user
        terceirizada = usuario.vinculo_atual.instituicao
        alteracoes_cardapio = terceirizada.alteracoes_cardapio_reprovadas
        page = self.paginate_queryset(alteracoes_cardapio)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # TODO rever os demais endpoints. Essa action consolida em uma única pesquisa as pesquisas por prioridade.
    @action(detail=False,
            url_path=f'{constants.PEDIDOS_DRE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        diretoria_regional = usuario.vinculo_atual.instituicao
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
