from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sme_pratoaberto_terceirizadas.permissao.permissoes import ValidarPermissao
from ..models import Permissao
from .serializers import PermissaoSerializer


class PermissaoViewSets(viewsets.ModelViewSet):
    queryset = Permissao.objects.all()
    serializer_class = PermissaoSerializer
    permission_classes = (IsAuthenticated, ValidarPermissao,)

    def list(self, request, *args, **kwargs):
        return Response({'Ola': 'Mundo meus amigos'})
