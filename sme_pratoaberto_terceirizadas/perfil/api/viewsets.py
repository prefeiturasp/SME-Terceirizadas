from notifications.models import Notification
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet

from .serializers import (
    PerfilPermissaoCreateSerializer, PerfilPermissaoSerializer,
    GrupoCompletoPerfilSerializer, NotificationSerializer,
    UsuarioSerializer, PerfilSerializer, GrupoPerfilCreateSerializer,
    PermissaoSerializer
)
from ..models import Usuario, Perfil, GrupoPerfil, Permissao, PerfilPermissao
from ..permissions import PodeMarcarComoLidaPermission


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


class NotificationViewSet(RetrieveModelMixin, GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    @action(detail=False)
    def minhas_notificacoes_nao_lidas(self, request):
        user = request.user
        notifications = user.notifications.unread()
        ser = self.get_serializer(notifications, many=True)
        return Response(ser.data)

    @action(detail=False)
    def minhas_notificacoes_lidas(self, request):
        user = request.user
        notifications = user.notifications.read()
        ser = self.get_serializer(notifications, many=True)
        return Response(ser.data)

    @action(detail=True, permission_classes=[PodeMarcarComoLidaPermission])
    def marcar_como_lida(self, request, pk):
        notificacao = self.get_object()
        notificacao.mark_as_read()
        ser = self.get_serializer(notificacao)
        return Response(ser.data)

    @action(detail=True, permission_classes=[PodeMarcarComoLidaPermission])
    def marcar_como_nao_lida(self, request, pk):
        notificacao = self.get_object()
        notificacao.mark_as_unread()
        ser = self.get_serializer(notificacao)
        return Response(ser.data)
