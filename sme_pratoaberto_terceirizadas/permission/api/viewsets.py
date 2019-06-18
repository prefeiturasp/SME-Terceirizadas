from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sme_pratoaberto_terceirizadas.permission.permissions import ValidatePermission
from ..models import Permission
from .serializers import ProfileSerializer


class PermissionViewSets(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, ValidatePermission,)

    def list(self, request, *args, **kwargs):
        return Response({'hello': 'World my friends'})
