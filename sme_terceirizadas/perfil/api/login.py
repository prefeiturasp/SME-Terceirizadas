import logging

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken

from sme_terceirizadas.perfil.services.autenticacao_service import AutenticacaoService

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(ObtainJSONWebToken):
    # Subistitui o login feito por /api-token-auth/

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):  # noqa
        login = request.data.get('login', '')
        senha = request.data.get('password', '')

        try:
            response = AutenticacaoService.autentica(login, senha)
            if response.status_code == 200:
                user_dict = response.json()
                if 'login' in user_dict.keys():
                    try:
                        user = User.objects.get(username=user_dict['login'])
                        user.name = user_dict['nome']
                        user.email = user_dict['email']
                        user.set_password(senha)
                        user.save()
                    except User.DoesNotExist:
                        logger.info('Usuário %s não encontrado.', login)
                        return Response({'data': {'detail': 'Usuário não encontrado.'}},
                                        status=status.HTTP_401_UNAUTHORIZED)

                    if not user.is_active or not user.existe_vinculo_ativo:
                        logger.info('Usuário %s inativo no Admin do sistema ou sem vinculo ativo.', login)
                        return Response({'detail': 'Você está sem autorização de acesso à aplicação no momento. '
                                                   'Entre em contato com o administrador do SIGPAE.'},
                                        status=status.HTTP_401_UNAUTHORIZED)

                    request._full_data = {'username': user_dict['login'], 'password': senha}
                    resp = super().post(request, *args, **kwargs)
                    data = {**user_dict, **resp.data}
                    return Response(data)
            return Response(response.json(), response.status_code)
        except Exception as e:
            return Response({'data': {'detail': f'ERROR - {e}'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
