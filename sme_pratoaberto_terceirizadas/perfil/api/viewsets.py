from rest_framework import viewsets

from sme_pratoaberto_terceirizadas.perfil.serializers import PublicUserSerializer
from ..models import Usuario


class UserViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = PublicUserSerializer
