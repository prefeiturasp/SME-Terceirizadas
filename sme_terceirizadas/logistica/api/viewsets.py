from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from sme_terceirizadas.dados_comuns.parser_xml import ListXMLParser
from sme_terceirizadas.logistica.api.serializers.serializer_create import SolicitacaoRemessaCreateSerializer
from sme_terceirizadas.logistica.api.serializers.serializers import (
    SolicitacaoRemessaSerializer,
    XmlParserSolicitacaoSerializer
)
from sme_terceirizadas.logistica.models import SolicitacaoRemessa

STR_XML_BODY = '{http://schemas.xmlsoap.org/soap/envelope/}Body'
STR_ARQUIVO_SOLICITACAO = 'ArqSolicitacaoMOD'


class SolicitacaoModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'delete']
    queryset = SolicitacaoRemessa.objects.all()
    serializer_class = SolicitacaoRemessaCreateSerializer
    permission_classes = [AllowAny]
    parser_classes = (ListXMLParser,)

    def get_serializer_class(self):
        if self.action == 'create':
            return XmlParserSolicitacaoSerializer
        return SolicitacaoRemessaSerializer

    def create(self, request, *args, **kwargs):
        remove_dirt = request.data.get(f'{STR_XML_BODY}')
        json_data = remove_dirt.pop(f'{STR_ARQUIVO_SOLICITACAO}')
        instance = SolicitacaoRemessaCreateSerializer().create(validated_data=json_data)
        serializer = SolicitacaoRemessaSerializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
