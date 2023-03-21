import logging

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken
from utility.carga_dados.perfil.importa_dados import ProcessaPlanilhaUsuarioServidorCoreSSO
from utility.carga_dados.perfil.schemas import ImportacaoPlanilhaUsuarioServidorCoreSSOSchema

from sme_terceirizadas.dados_comuns.constants import ADMINISTRADOR_UE, DIRETOR_UE
from sme_terceirizadas.eol_servico.utils import EOLException, EOLServicoSGP
from sme_terceirizadas.escola.services import NovoSGPServicoLogado, NovoSGPServicoLogadoException
from sme_terceirizadas.perfil.models import Perfil
from sme_terceirizadas.perfil.services.autenticacao_service import AutenticacaoService

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(ObtainJSONWebToken):
    # Subistitui o login feito por /api-token-auth/

    permission_classes = (permissions.AllowAny,)

    def checa_login_senha_coresso(self, login, senha):
        novo_sgp = NovoSGPServicoLogado()
        response_login = novo_sgp.pegar_token_acesso(login, senha)
        if response_login.status_code != status.HTTP_200_OK or len(login) != 7:
            raise NovoSGPServicoLogadoException('Usuário não encontrado')

    def update_user(self, user_dict, senha):
        user = User.objects.get(username=user_dict['login'])
        if not user.is_active or not user.existe_vinculo_ativo:
            raise PermissionDenied('Você está sem autorização de acesso à aplicação no momento. '
                                   'Entre em contato com o administrador do SIGPAE.')
        last_login = user.last_login
        user.name = user_dict['nome']
        user.email = user_dict['email']
        user.set_password(senha)
        user.save()
        return user, last_login

    def build_response_data(self, request, user_dict, senha, last_login, args, kwargs):
        request._full_data = {'username': user_dict['login'], 'password': senha}
        resp = super().post(request, *args, **kwargs)
        data = {'last_login': last_login, **user_dict, **resp.data}
        return data

    def cria_usuario(self, dados_usuario, nome_perfil):
        tupla_dados = (
            dados_usuario['cargos'][0]['codigoUnidade'],
            dados_usuario['nome'],
            dados_usuario['cargos'][0]['descricaoCargo'].strip(),
            dados_usuario['email'],
            dados_usuario['cpf'],
            dados_usuario['rf'],
            'escola',
            nome_perfil,
            ''
        )
        processador = ProcessaPlanilhaUsuarioServidorCoreSSO(None, None)
        dados_formatados = processador.monta_dicionario_de_dados(tupla_dados)
        usuario_schema = ImportacaoPlanilhaUsuarioServidorCoreSSOSchema(**dados_formatados)
        processador.cria_usuario_servidor(0, usuario_schema)

    def get_dados_usuario_json(self, login):
        response_dados_usuario = EOLServicoSGP.get_dados_usuario(login)
        dados_usuario = response_dados_usuario.json()
        if response_dados_usuario.status_code != status.HTTP_200_OK:
            raise EOLException('Usuário não encontrado')
        return dados_usuario

    def usuario_com_cargo_de_acesso_automatico(self, dados_usuario):
        return (dados_usuario['cargos'][0]['codigoCargo'] in
                [cargo['codigo'] for cargo in Perfil.cargos_diretor() + Perfil.cargos_adm_escola()])

    def usuario_com_cargo_diretor(self, dados_usuario):
        return (dados_usuario['cargos'][0]['codigoCargo'] in
                [cargo['codigo'] for cargo in Perfil.cargos_diretor()])

    def usuario_com_cargo_adm_escola(self, dados_usuario):
        return (dados_usuario['cargos'][0]['codigoCargo'] in
                [cargo['codigo'] for cargo in Perfil.cargos_adm_escola()])

    def checa_se_cria_usuario(self, dados_usuario):
        if not self.usuario_com_cargo_de_acesso_automatico(dados_usuario):
            raise NovoSGPServicoLogadoException('Usuário não possui permissão de acesso ao SIGPAE')
        if self.usuario_com_cargo_diretor(dados_usuario):
            self.cria_usuario(dados_usuario, DIRETOR_UE)
        elif self.usuario_com_cargo_adm_escola(dados_usuario):
            self.cria_usuario(dados_usuario, ADMINISTRADOR_UE)

    def post(self, request, *args, **kwargs):
        login = request.data.get('login', '')
        senha = request.data.get('password', '')
        try:
            response = AutenticacaoService.autentica(login, senha)
            user_dict = response.json()
            if 'login' in user_dict.keys():
                user, last_login = self.update_user(user_dict, senha)
                data = self.build_response_data(request, user_dict, senha, last_login, args, kwargs)
                return Response(data)
            else:
                self.checa_login_senha_coresso(login, senha)
                dados_usuario = self.get_dados_usuario_json(login)
                self.checa_se_cria_usuario(dados_usuario)
                user_dict = {'login': login, **dados_usuario}
                user, last_login = self.update_user(user_dict, senha)
                data = self.build_response_data(request, user_dict, senha, last_login, args, kwargs)
                return Response(data)
        except User.DoesNotExist:
            logger.info('Usuário %s não encontrado.', login)
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_401_UNAUTHORIZED)
        except (NovoSGPServicoLogadoException, PermissionDenied) as e:
            logger.info(str(e), login)
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except EOLException as e:
            logger.info(str(e), login)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
