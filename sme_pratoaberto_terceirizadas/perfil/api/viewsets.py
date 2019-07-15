from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from sme_pratoaberto_terceirizadas.perfil.api.serializers import PerfilPermissaoCreateSerializer, \
    PerfilPermissaoSerializer, GrupoCompletoPerfilSerializer
from sme_pratoaberto_terceirizadas.perfil.models.perfil import PerfilPermissao
from .serializers import UsuarioSerializer, PerfilSerializer, GrupoPerfilCreateSerializer, PermissaoSerializer
from ..models import Usuario, Perfil, GrupoPerfil, Permissao


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class PerfilViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer


class GrupoPerfilViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = GrupoPerfil.objects.all()
    serializer_class = GrupoCompletoPerfilSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GrupoPerfilCreateSerializer
        return GrupoCompletoPerfilSerializer


class PermissaoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Permissao.objects.all()
    serializer_class = PermissaoSerializer


class AcoesViewSet(ViewSet):
    def list(self, request):
        return Response(dict(PerfilPermissao.ACOES))


class PerfilPermissaoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = PerfilPermissao.objects.all()
    serializer_class = PerfilPermissaoSerializer

    # TODO: permitir deletar somente se o status for do inicial...
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PerfilPermissaoCreateSerializer
        return PerfilPermissaoSerializer
