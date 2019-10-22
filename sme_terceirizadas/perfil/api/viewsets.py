from django.contrib.auth.tokens import default_token_generator
from notifications.models import Notification
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from .permissions import PodeMarcarDesmarcarComoLidaPermission
from .serializers import (
    GrupoCompletoPerfilSerializer, GrupoPerfilCreateSerializer, NotificationSerializer, PerfilPermissaoCreateSerializer,
    PerfilPermissaoSerializer, PerfilSerializer, PermissaoSerializer, UsuarioUpdateSerializer, UsuarioSerializer
)
from ..models import GrupoPerfil, Perfil, PerfilPermissao, Permissao, Usuario
from ...escola.api.serializers import UsuarioDetalheSerializer


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Usuario.objects.all()
    serializer_class = UsuarioDetalheSerializer

    @action(detail=False, url_path='meus-dados')
    def meus_dados(self, request):
        usuario = request.user
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)


class UsuarioUpdateViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UsuarioUpdateSerializer
    token_generator = default_token_generator

    def create(self, request, *args, **kwargs):
        usuario = Usuario.objects.get(registro_funcional=request.data.get('registro_funcional'))
        usuario = UsuarioUpdateSerializer(usuario).partial_update(request.data, usuario)
        return Response(UsuarioDetalheSerializer(usuario).data)


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
