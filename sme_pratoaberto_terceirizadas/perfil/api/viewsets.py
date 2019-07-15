from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .serializers import UsuarioSerializer, PerfilSerializer, GrupoCompletoPerfilSerializer, PermissaoSerializer
from ..models import Usuario, Perfil, GrupoPerfil, Permissao


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
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


class PermissaoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Permissao.objects.all()
    serializer_class = PermissaoSerializer


class AcoesViewSet(ViewSet):
    # permission_classes = (AllowAny,)

    def list(self, request):
        return Response(dict(Permissao.ACOES))
