from typing import Any

from des.models import DynamicEmailConfiguration
from django.db import IntegrityError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from .serializers import DiasUteisSerializer, ConfiguracaoEmailSerializer
from ..models import DiasUteis
from ..utils import obter_dias_uteis_apos


class DiasUteisViewSet(ViewSet):
    permission_classes = ()
    serializer_class = DiasUteisSerializer

    def list(self, request):
        dias_uteis = {
            1: DiasUteis(
                data_cinco_dias_uteis=obter_dias_uteis_apos(5).strftime('%d/%m/%Y'),
                data_dois_dias_uteis=obter_dias_uteis_apos(2).strftime('%d/%m/%Y'))
        }
        serializer = DiasUteisSerializer(
            instance=dias_uteis.values(), many=True)
        return Response(serializer.data)


class ConfiguracaoEmailViewSet(ModelViewSet):
    queryset = DynamicEmailConfiguration.objects.all()
    serializer_class = ConfiguracaoEmailSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(data={'error': 'A configuração já existe, tente usar o método PUT',
                                  'detail': '{}'.format(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().update(request, *args, **kwargs)
