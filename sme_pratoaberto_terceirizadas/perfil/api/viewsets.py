from rest_framework import viewsets

from .serializers import UsuarioSerializer, PerfilSerializer, GrupoCompletoPerfilSerializer
from ..models import Usuario, Perfil, GrupoPerfil


class UsusarioViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class PerfilViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer


class GrupoPerfilViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = GrupoPerfil.objects.all()
    serializer_class = GrupoCompletoPerfilSerializer
