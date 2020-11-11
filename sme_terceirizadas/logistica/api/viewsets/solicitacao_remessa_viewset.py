from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_xml.parsers import XMLParser


class ExampleView(APIView):
    """
    A view that can accept POST requests with XML content.
    """
    permission_classes = [AllowAny]
    parser_classes = (XMLParser,)

    @property
    def get_extra_actions(cls):
        return []

    def post(self, request, format=None):
        print(request)
        import ipdb
        ipdb.set_trace()
        return Response({'received data': request.DATA})
