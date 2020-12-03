from django.db.utils import DataError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_406_NOT_ACCEPTABLE
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.fluxo_status import SolicitacaoRemessaWorkFlow
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.dados_comuns.parser_xml import ListXMLParser
from sme_terceirizadas.dados_comuns.permissions import UsuarioDilogCodae
from sme_terceirizadas.logistica.api.serializers.serializer_create import SolicitacaoRemessaCreateSerializer
from sme_terceirizadas.logistica.api.serializers.serializers import (
    SolicitacaoRemessaLookUpSerializer,
    SolicitacaoRemessaSerializer,
    SolicitacaoRemessaSimplesSerializer,
    XmlParserSolicitacaoSerializer
)
from sme_terceirizadas.logistica.models import SolicitacaoRemessa

STR_XML_BODY = '{http://schemas.xmlsoap.org/soap/envelope/}Body'
STR_ARQUIVO_SOLICITACAO = 'ArqSolicitacaoMOD'


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
        json_data = remove_dirt.pop(f'{STR_ARQUIVO_SOLICITACAO}')
        try:
            instance = SolicitacaoRemessaCreateSerializer().create(validated_data=json_data)
            usuario = request.user

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
