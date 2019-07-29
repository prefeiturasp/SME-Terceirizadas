from notifications.models import Notification
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet

from .permissions import PodeMarcarDesmarcarComoLidaPermission
from .serializers import (
    PerfilPermissaoCreateSerializer, PerfilPermissaoSerializer,
    GrupoCompletoPerfilSerializer, NotificationSerializer,
    UsuarioSerializer, PerfilSerializer, GrupoPerfilCreateSerializer,
    PermissaoSerializer
)
from ..models import Usuario, Perfil, GrupoPerfil, Permissao, PerfilPermissao


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
        page = self.paginate_queryset(notifications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False)
    def minhas_notificacoes_lidas(self, request):
        user = request.user
        notifications = user.notifications.read()
        page = self.paginate_queryset(notifications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[PodeMarcarDesmarcarComoLidaPermission])
    def marcar_lido(self, request, pk):
        notificacao = self.get_object()
        notificacao.mark_as_read()
        serializer = self.get_serializer(notificacao)
        return Response(serializer.data)

    @action(detail=True, permission_classes=[PodeMarcarDesmarcarComoLidaPermission])
    def desmarcar_lido(self, request, pk):
        notificacao = self.get_object()
        notificacao.mark_as_unread()
        serializer = self.get_serializer(notificacao)
        return Response(serializer.data)
