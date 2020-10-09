import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ...escola.api.serializers import UsuarioDetalheSerializer
from ...terceirizada.models import Terceirizada
from ..api.helpers import ofuscar_email
from ..models import Perfil, Usuario
from ..tasks import busca_cargo_de_usuario
from .serializers import PerfilSerializer, UsuarioUpdateSerializer


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'
    queryset = Usuario.objects.all()
    serializer_class = UsuarioDetalheSerializer

    @action(detail=False, url_path='atualizar-email', methods=['patch'])
    def atualizar_email(self, request):
        usuario = request.user
        tipo_email = request.data.get('tipo_email')
        usuario.tipo_email = tipo_email
        usuario.email = request.data.get('email')
        usuario.save()
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

    @action(detail=False, url_path='atualizar-cargo', methods=['get'])
    def atualizar_cargo(self, request):
        usuario = request.user
        registro_funcional = usuario.registro_funcional
        busca_cargo_de_usuario.delay(registro_funcional)
        return Response({'detail': 'sucesso'}, status=status.HTTP_200_OK)

    @action(detail=False, url_path='atualizar-senha', methods=['patch'])
    def atualizar_senha(self, request):
        try:
            usuario = request.user
            assert usuario.check_password(request.data.get(
                'senha_atual')) is True, 'senha atual incorreta'
            senha = request.data.get('senha')
            confirmar_senha = request.data.get('confirmar_senha')
            assert senha == confirmar_senha, 'senha e confirmar senha divergem'
            usuario.set_password(senha)
            usuario.save()
            serializer = self.get_serializer(usuario)
        except AssertionError as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    @action(detail=False, url_path='meus-dados')
    def meus_dados(self, request):
        usuario = request.user
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)


class UsuarioUpdateViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UsuarioUpdateSerializer

    def get_authenticators(self, *args, **kwargs):
        if 'post' in self.action_map and self.action_map['post'] == 'create':
            return []
        return super().get_authenticators(*args, **kwargs)

    def _get_usuario(self, request):
        if request.data.get('registro_funcional') is not None:
            return Usuario.objects.get(registro_funcional=request.data.get('registro_funcional'))
        else:
            return Usuario.objects.get(email=request.data.get('email'))

    def _get_usuario_por_rf_email(self, registro_funcional_ou_email):
        return Usuario.objects.get(
            Q(registro_funcional=registro_funcional_ou_email) |  # noqa W504
            Q(email=registro_funcional_ou_email)
        )

    def create(self, request):  # noqa C901
        try:
            usuario = self._get_usuario(request)
            # TODO: ajeitar isso aqui
            usuario = UsuarioUpdateSerializer(
                usuario).partial_update(usuario, request.data)
            if not isinstance(usuario.vinculo_atual.instituicao, Terceirizada):
                usuario.enviar_email_confirmacao()
            return Response(UsuarioDetalheSerializer(usuario).data)
        except ValidationError as e:
            return Response({'detail': e.detail[0].title()}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'detail': 'E-mail não cadastrado no sistema'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, url_path='recuperar-senha/(?P<registro_funcional_ou_email>.*)')
    def recuperar_senha(self, request, registro_funcional_ou_email=None):
        try:
            usuario = self._get_usuario_por_rf_email(
                registro_funcional_ou_email)
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
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer


class UsuarioConfirmaEmailViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
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
            vinculo_esperando_ativacao = usuario.vinculos.get(
                ativo=False, data_inicial=None, data_final=None)
            vinculo_esperando_ativacao.ativo = True
            vinculo_esperando_ativacao.data_inicial = datetime.date.today()
            vinculo_esperando_ativacao.save()
        except ObjectDoesNotExist:
            return Response({'detail': 'Não possui vínculo'},
                            status=status.HTTP_400_BAD_REQUEST)

        usuario.save()
        return Response(UsuarioDetalheSerializer(usuario).data)
