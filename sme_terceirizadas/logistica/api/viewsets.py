from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DataError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_406_NOT_ACCEPTABLE
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.fluxo_status import SolicitacaoRemessaWorkFlow
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.dados_comuns.parser_xml import ListXMLParser
from sme_terceirizadas.dados_comuns.permissions import UsuarioDilogCodae
from sme_terceirizadas.logistica.api.serializers.serializer_create import SolicitacaoRemessaCreateSerializer
from sme_terceirizadas.logistica.api.serializers.serializers import (
    AlimentoDaGuiaDaRemessaSerializer,
    AlimentoDaGuiaDaRemessaSimplesSerializer,
    GuiaDaRemessaSerializer,
    GuiaDaRemessaSimplesSerializer,
    InfoUnidadesSimplesDaGuiaSerializer,
    SolicitacaoRemessaLookUpSerializer,
    SolicitacaoRemessaSerializer,
    SolicitacaoRemessaSimplesSerializer,
    XmlParserSolicitacaoSerializer
)
from sme_terceirizadas.logistica.models import Alimento
from sme_terceirizadas.logistica.models import Guia as GuiasDasRequisicoes
from sme_terceirizadas.logistica.models import SolicitacaoRemessa

from ..utils import RequisicaoPagination
from .helpers import remove_acentos_de_strings, retorna_status_das_requisicoes

STR_XML_BODY = '{http://schemas.xmlsoap.org/soap/envelope/}Body'
STR_ARQUIVO_SOLICITACAO = 'ArqSolicitacaoMOD'
STR_ARQUIVO_CANCELAMENTO = 'ArqCancelamento'


class SolicitacaoEnvioEmMassaModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    http_method_names = ['post']
    queryset = SolicitacaoRemessa.objects.all()
    serializer_class = SolicitacaoRemessaCreateSerializer
    permission_classes = [UsuarioDilogCodae]
    pagination_class = None

    @action(detail=False, permission_classes=(UsuarioDilogCodae,),
            methods=['post'], url_path='envia-grade')
    def inicia_fluxo_solicitacoes_em_massa(self, request):
        usuario = request.user
        solicitacoes = request.data.get('solicitacoes', [])
        solicitacoes = SolicitacaoRemessa.objects.filter(uuid__in=solicitacoes,
                                                         status=SolicitacaoRemessaWorkFlow.AGUARDANDO_ENVIO)
        for solicitacao in solicitacoes:
            try:
                solicitacao.inicia_fluxo(user=usuario)
            except InvalidTransitionError as e:
                return Response(dict(detail=f'Erro de transição de estado: {e}', status=HTTP_400_BAD_REQUEST))
        serializer = SolicitacaoRemessaSerializer(solicitacoes, many=True)
        return Response(serializer.data)


class SolicitacaoCancelamentoModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    http_method_names = ['post', ]
    queryset = SolicitacaoRemessa.objects.all()
    serializer_class = XmlParserSolicitacaoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (ListXMLParser,)
    pagination_class = None

    def cancela_guias(self, num_solicitacao, guias, usuario):
        # Cancela as guias recebidas no cancelamento;
        # Se as guias da solicitação forem todas as guias recebidas, cancela também a solicitação;
        # E se todas as guias de uma solicitação encontram se canceladas, cancela também a solicitação;

        if isinstance(guias, list):
            guias_payload = [x['StrNumGui'] for x in guias]
        else:
            guias_payload = [x['StrNumGui'] for x in guias.values()]

        solicitacao = SolicitacaoRemessa.objects.get(numero_solicitacao=num_solicitacao)
        solicitacao.guias.filter(numero_guia__in=guias_payload).update(status=SolicitacaoRemessaWorkFlow.PAPA_CANCELA)

        guias_existentes = list(solicitacao.guias.values_list('numero_guia', flat=True))
        existe_guia_nao_cancelada = solicitacao.guias.exclude(status=GuiasDasRequisicoes.STATUS_CANCELADA).exists()

        if set(guias_existentes) == set(guias_payload) or not existe_guia_nao_cancelada:
            solicitacao.cancela_solicitacao(user=usuario)
        else:
            solicitacao.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.PAPA_CANCELA_SOLICITACAO,
                                             usuario=usuario,
                                             justificativa=f'Guias canceladas: {guias_payload}')

    def create(self, request, *args, **kwargs):  # noqa: C901
        remove_dirt = request.data.get(f'{STR_XML_BODY}')
        json_cancelamento = remove_dirt.get(f'{STR_ARQUIVO_CANCELAMENTO}')
        usuario = request.user

        if json_cancelamento:
            try:
                num_solicitacao = json_cancelamento['StrNumSol']
                guias = json_cancelamento['guias']
                self.cancela_guias(num_solicitacao, guias, usuario)

                return Response(dict(detail=f'Cancelamento realizado com sucesso', status=True),
                                status=HTTP_200_OK)
            except InvalidTransitionError as e:
                return Response(dict(detail=f'Erro de transição de estado: {e}', status=False),
                                status=HTTP_406_NOT_ACCEPTABLE)
            except ObjectDoesNotExist as e:
                return Response(dict(detail=f'Erro de transição de estado: {e}', status=False),
                                status=HTTP_406_NOT_ACCEPTABLE)


class SolicitacaoModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'patch']
    queryset = SolicitacaoRemessa.objects.all()
    serializer_class = SolicitacaoRemessaCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (ListXMLParser,)
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'create':
            return XmlParserSolicitacaoSerializer
        if self.action == 'list':
            return SolicitacaoRemessaLookUpSerializer
        return SolicitacaoRemessaSerializer

    def create(self, request, *args, **kwargs):
        remove_dirt = request.data.get(f'{STR_XML_BODY}')
        json_data = remove_dirt.get(f'{STR_ARQUIVO_SOLICITACAO}')
        usuario = request.user

        if json_data:
            try:
                instance = SolicitacaoRemessaCreateSerializer().create(validated_data=json_data)

                instance.salvar_log_transicao(
                    status_evento=LogSolicitacoesUsuario.INICIO_FLUXO_SOLICITACAO,
                    usuario=usuario
                )

                return Response(dict(detail=f'Criado com sucesso', status=True),
                                status=HTTP_201_CREATED)
            except DataError as e:
                return Response(dict(detail=f'Erro de transição de estado: {e}', status=False),
                                status=HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=['GET'], url_path='lista-numeros')
    def lista_numeros(self, request):
        queryset = self.get_queryset().filter(status__in=[SolicitacaoRemessaWorkFlow.AGUARDANDO_ENVIO])
        response = {'results': SolicitacaoRemessaSimplesSerializer(queryset, many=True).data}
        return Response(response)

    @action(detail=False, permission_classes=(UsuarioDilogCodae,),  # noqa C901
            methods=['GET'], url_path='lista-requisicoes-para-envio')
    def lista_requisicoes_para_envio(self, request):
        queryset = self.queryset.filter(status=SolicitacaoRemessaWorkFlow.AGUARDANDO_ENVIO)
        numero_requisicao = request.query_params.get('numero_requisicao', None)
        nome_distribuidor = request.query_params.get('nome_distribuidor', None)
        data_inicio = request.query_params.get('data_inicio', None)
        data_fim = request.query_params.get('data_fim', None)

        if numero_requisicao:
            queryset = queryset.filter(numero_solicitacao=numero_requisicao)
        if nome_distribuidor:
            queryset = queryset.filter(distribuidor__nome_fantasia__icontains=nome_distribuidor)
        if data_inicio and data_fim:
            queryset = queryset.filter(guias__data_entrega__range=[data_inicio, data_fim]).distinct()
        if data_inicio and not data_fim:
            queryset = queryset.filter(guias__data_entrega__gte=data_inicio).distinct()
        if data_fim and not data_inicio:
            queryset = queryset.filter(guias__data_entrega__lte=data_fim).distinct()

        response = {'results': SolicitacaoRemessaLookUpSerializer(queryset, many=True).data}
        return Response(response)

    @action(detail=False, permission_classes=(UsuarioDilogCodae,),  # noqa C901
            methods=['GET'], url_path='consulta-requisicoes-de-entrega')
    def lista_requisicoes_filtro_avancado(self, request):
        queryset = self.get_queryset()
        numero_requisicao = request.query_params.get('numero_requisicao', None)
        status = request.query_params.get('status', [])
        data_inicio = request.query_params.get('data_inicio', None)
        data_fim = request.query_params.get('data_fim', None)
        numero_guia = request.query_params.get('numero_guia', None)
        nome_produto = request.query_params.get('nome_produto', None)
        nome_distribuidor = request.query_params.get('nome_distribuidor', None)
        codigo_eol = request.query_params.get('codigo_escola', None)
        nome_escola = request.query_params.get('nome_escola', None)
        if len(status) >= 1:
            lista_status = retorna_status_das_requisicoes(status)
            queryset = queryset.filter(numero_status__in=lista_status)
        if numero_requisicao:
            queryset = queryset.filter(numero_solicitacao=numero_requisicao)
        if nome_distribuidor:
            queryset = queryset.filter(distribuidor__nome_fantasia__icontains=nome_distribuidor)
        if numero_guia:
            queryset = queryset.filter(guias__numero_guia__icontains=numero_guia).distinct()
        if data_inicio:
            queryset = queryset.filter(guias__data_entrega__gte=data_inicio).distinct()
        if data_fim:
            queryset = queryset.filter(guias__data_entrega__lte=data_fim).distinct()
        if codigo_eol:
            queryset = queryset.filter(guias__codigo_unidade__icontains=codigo_eol).distinct()
        if nome_escola:
            unidade_educacional = remove_acentos_de_strings(nome_escola)
            queryset = queryset.filter(guias__nome_unidade__icontains=unidade_educacional).distinct()
        if nome_produto:
            produto = remove_acentos_de_strings(nome_produto)
            queryset = queryset.filter(guias__alimentos__nome_alimento__icontains=produto).distinct()

        self.pagination_class = RequisicaoPagination
        page = self.paginate_queryset(queryset)
        serializer = SolicitacaoRemessaSerializer(
            page if page is not None else queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=(UsuarioDilogCodae,),
            methods=['patch'], url_path='envia-solicitacao')
    def incia_fluxo_solicitacao(self, request, uuid=None):
        solicitacao = SolicitacaoRemessa.objects.get(uuid=uuid,
                                                     status=SolicitacaoRemessaWorkFlow.AGUARDANDO_ENVIO)
        usuario = request.user

        try:
            solicitacao.inicia_fluxo(user=usuario, )
            serializer = SolicitacaoRemessaSerializer(solicitacao)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=(UsuarioDilogCodae,),
            methods=['patch'], url_path='distribuidor-confirma')
    def distribuidor_confirma_hook(self, request, uuid=None):
        solicitacao = SolicitacaoRemessa.objects.get(uuid=uuid)
        usuario = request.user

        try:
            solicitacao.empresa_atende(user=usuario, )
            serializer = SolicitacaoRemessaSerializer(solicitacao)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)


class GuiaDaRequisicaoModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = GuiasDasRequisicoes.objects.all()
    serializer_class = GuiaDaRemessaSerializer
    permission_classes = [UsuarioDilogCodae]

    @action(detail=False, methods=['GET'], url_path='lista-numeros')
    def lista_numeros(self, request):
        response = {'results': GuiaDaRemessaSimplesSerializer(self.get_queryset(), many=True).data}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='unidades-escolares')
    def nomes_unidades(self, request):
        unidades_escolares = GuiasDasRequisicoes.objects.values(
            'nome_unidade', 'codigo_unidade').distinct()
        response = {'results': InfoUnidadesSimplesDaGuiaSerializer(unidades_escolares, many=True).data}
        return Response(response)


class AlimentoDaGuiaModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Alimento.objects.all()
    serializer_class = AlimentoDaGuiaDaRemessaSerializer
    permission_classes = [UsuarioDilogCodae]

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_nomes(self, request):
        response = {'results': AlimentoDaGuiaDaRemessaSimplesSerializer(self.get_queryset(), many=True).data}
        return Response(response)
