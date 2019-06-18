from typing import Any

from des.models import DynamicEmailConfiguration
from django.db import IntegrityError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from .serializers import WorkingDaysSerializer, EmailConfigurationSerializer
from ..models import WorkingDays
from ..utils import obter_dias_uteis_apos


class WorkingDaysViewSet(ViewSet):
    permission_classes = ()
    serializer_class = WorkingDaysSerializer

    def list(self, request):
        working_days = {
            1: WorkingDays(
                date_five_working_days=obter_dias_uteis_apos(5).strftime('%d/%m/%Y'),
                date_two_working_days=obter_dias_uteis_apos(2).strftime('%d/%m/%Y'))
        }
        serializer = WorkingDaysSerializer(
            instance=working_days.values(), many=True)
        return Response(serializer.data)


class EmailConfigurationViewSet(ModelViewSet):
    queryset = DynamicEmailConfiguration.objects.all()
    serializer_class = EmailConfigurationSerializer

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
