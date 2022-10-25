from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ..utils import SAFIException, SAFIService


class DadosContratoSAFIViewSet(ViewSet):
    lookup_field = 'contrato_uuid'
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, contrato_uuid=None):
        try:
            safiservice = SAFIService()
            contrato = safiservice.get_contrato(contrato_uuid)
            return Response(contrato)
        except SAFIException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='lista-termos-de-contratos')
    def lista_termos_de_contratos(self, request):
        try:
            safiservice = SAFIService()
            resultado = safiservice.get_termos_de_contratos()
            return Response(resultado)
        except SAFIException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
