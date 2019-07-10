from typing import Any

from des.models import DynamicEmailConfiguration
from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet, ReadOnlyModelViewSet

from .serializers import ConfiguracaoEmailSerializer, DiaSemanaSerializer
from ..models import DiaSemana
from ..utils import obter_dias_uteis_apos_hoje


class DiasDaSemanaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'id'
    queryset = DiaSemana.objects.all()
    serializer_class = DiaSemanaSerializer


class DiasUteisViewSet(ViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        dias_uteis = {
            'proximos_cinco_dias_uteis': obter_dias_uteis_apos_hoje(5),
            'proximos_dois_dias_uteis': obter_dias_uteis_apos_hoje(2)
        }

        return Response(dias_uteis)


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
