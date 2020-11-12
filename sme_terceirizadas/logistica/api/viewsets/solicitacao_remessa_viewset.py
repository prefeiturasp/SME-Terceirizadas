from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from sme_terceirizadas.dados_comuns.parser_xml import ListXMLParser


class ExampleView(APIView):
    """
    A view that can accept POST requests with XML content.
    """
    permission_classes = [AllowAny]
    parser_classes = (ListXMLParser,)

    @property
    def get_extra_actions(cls):
        return []

    def post(self, request, format=None):

        return Response({'received data': request.data})
