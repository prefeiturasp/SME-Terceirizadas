from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import AlteracaoCardapioSerializer
from ..models import AlteracaoCardapio


class AlteracaoCardapioViewSet(ModelViewSet):
    queryset = AlteracaoCardapio.objects.all()
    serializer_class = AlteracaoCardapioSerializer
    lookup_field = 'uuid'

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        retval = super().create(request, *args, **kwargs)
        if retval:
            print('disparando notificação para a DRE...')
        return retval
