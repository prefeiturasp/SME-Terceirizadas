import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    PerfilSerializer, UsuarioUpdateSerializer
)
from ..api.helpers import ofuscar_email
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

    def _get_usuario_por_rf_email(self, registro_funcional_ou_email):
        return Usuario.objects.get(
            Q(registro_funcional=registro_funcional_ou_email) |  # noqa W504
            Q(email=registro_funcional_ou_email)
        )

    def create(self, request):
        try:
            usuario = self._get_usuario(request)
        except ObjectDoesNotExist:
            return Response({'detail': 'Erro ao cadastrar usuário'},
                            status=status.HTTP_400_BAD_REQUEST)
        usuario = UsuarioUpdateSerializer(usuario).partial_update(usuario, request.data)
        usuario.enviar_email_confirmacao()
        return Response(UsuarioDetalheSerializer(usuario).data)

    @action(detail=False, url_path='recuperar-senha/(?P<registro_funcional_ou_email>.*)')
    def recuperar_senha(self, request, registro_funcional_ou_email=None):
        try:
            usuario = self._get_usuario_por_rf_email(registro_funcional_ou_email)
        except ObjectDoesNotExist:
            return Response({'detail': 'Não existe usuário com este e-mail ou RF'},
                            status=status.HTTP_400_BAD_REQUEST)
        usuario.enviar_email_recuperacao_senha()
        return Response({'email': f'{ofuscar_email(usuario.email)}'})

    @action(detail=False, methods=['POST'], url_path='atualizar-senha/(?P<usuario_uuid>.*)/(?P<token_reset>.*)')  # noqa
    def atualizar_senha(self, request, usuario_uuid=None, token_reset=None):
        # TODO: melhorar este método
        senha1 = request.data.get('senha1')
        senha2 = request.data.get('senha2')
        if senha1 != senha2:
            return Response({'detail': 'Senhas divergem'}, status.HTTP_400_BAD_REQUEST)
        try:
            usuario = Usuario.objects.get(uuid=usuario_uuid)
        except ObjectDoesNotExist:
            return Response({'detail': 'Não existe usuário com este e-mail ou RF'},
                            status=status.HTTP_400_BAD_REQUEST)
        if usuario.atualiza_senha(senha=senha1, token=token_reset):
            return Response({'sucesso!': 'senha atualizada com sucesso'})
        else:
            return Response({'detail': 'Token inválido'}, status.HTTP_400_BAD_REQUEST)


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
