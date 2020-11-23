from django.db.utils import DataError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from xworkflows import InvalidTransitionError

from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.dados_comuns.parser_xml import ListXMLParser
from sme_terceirizadas.dados_comuns.permissions import UsuarioDilogCodae
from sme_terceirizadas.logistica.api.serializers.serializer_create import SolicitacaoRemessaCreateSerializer
from sme_terceirizadas.logistica.api.serializers.serializers import (
    SolicitacaoRemessaSerializer,
    XmlParserSolicitacaoSerializer,
    SolicitacaoRemessaLookUpSerializer
)
from sme_terceirizadas.logistica.models import SolicitacaoRemessa

STR_XML_BODY = '{http://schemas.xmlsoap.org/soap/envelope/}Body'
STR_ARQUIVO_SOLICITACAO = 'ArqSolicitacaoMOD'


class SolicitacaoModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'patch']
    queryset = SolicitacaoRemessa.objects.all()
    serializer_class = SolicitacaoRemessaCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (ListXMLParser,)

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
                            status=status.HTTP_201_CREATED)
        except DataError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}', status=False),
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, permission_classes=(UsuarioDilogCodae,),
            methods=['patch'], url_path='envia-solicitacao')
    def incia_fluxo_solicitacao(self, request, uuid=None):
        solicitacao = SolicitacaoRemessa.objects.get(uuid=uuid)
        usuario = request.user

        try:
            solicitacao.inicia_fluxo(user=usuario, )
            serializer = SolicitacaoRemessaSerializer(solicitacao)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

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
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)
