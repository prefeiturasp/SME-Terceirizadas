import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    PerfilSerializer, UsuarioUpdateSerializer
)
from ..models import Perfil, Usuario
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

    def _get_usuario(self, request):
        return Usuario.objects.get(registro_funcional=request.data.get('registro_funcional'))

    def create(self, request):
        try:
            usuario = self._get_usuario(request)
        except ObjectDoesNotExist:
            return Response({'detail': 'Erro ao cadastrar usuário'},
                            status=status.HTTP_400_BAD_REQUEST)
        usuario = UsuarioUpdateSerializer(usuario).partial_update(usuario, request.data)
        usuario.enviar_email_confirmacao()
        return Response(UsuarioDetalheSerializer(usuario).data)


class PerfilViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer


class UsuarioConfirmaEmailViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UsuarioDetalheSerializer

    # TODO: ajeitar isso
    def list(self, request, uuid, confirmation_key):  # noqa C901
        try:
            usuario = Usuario.objects.get(uuid=uuid)
            usuario.confirm_email(confirmation_key)
            usuario.is_active = usuario.is_confirmed
        except ObjectDoesNotExist:
            return Response({'detail': 'Erro ao confirmar email'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            vinculo_esperando_ativacao = usuario.vinculos.get(ativo=False, data_inicial=None, data_final=None)
            vinculo_esperando_ativacao.ativo = True
            vinculo_esperando_ativacao.data_inicial = datetime.date.today()
            vinculo_esperando_ativacao.save()
        except ObjectDoesNotExist:
            return Response({'detail': 'Não possui vínculo'},
                            status=status.HTTP_400_BAD_REQUEST)

        usuario.save()
        return Response(UsuarioDetalheSerializer(usuario).data)
