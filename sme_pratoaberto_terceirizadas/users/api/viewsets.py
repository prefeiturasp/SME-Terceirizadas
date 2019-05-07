from rest_framework import viewsets

from sme_pratoaberto_terceirizadas.users.serializers import PublicUserSerializer
from ..models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
