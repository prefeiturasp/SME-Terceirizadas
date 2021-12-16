import environ
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from rest_framework import exceptions
from spyne.application import Application
from spyne.decorator import rpc
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.service import ServiceBase

from sme_terceirizadas.eol_servico.utils import EOLException

from ....dados_comuns.models import LogSolicitacoesUsuario
from .models import ArqCancelamento, ArqSolicitacaoMOD, SoapResponse, oWsAcessoModel
from .token_auth import TokenAuthentication

env = environ.Env()

API_URL = env.str('API_URL', default=None)
NS = f'{env("DJANGO_XMLNS")}'


class SolicitacaoService(ServiceBase):

    @rpc(oWsAcessoModel, ArqSolicitacaoMOD, _returns=SoapResponse) # noqa C901
    def Solicitacao(ctx, oWsAcessoModel, ArqSolicitacaoMOD):

        try:
            user, token = TokenAuthentication().authenticate(oWsAcessoModel)

        except exceptions.AuthenticationFailed as e:
            return SoapResponse(str_status='false', str_menssagem=str(e))

        try:
            solicitacao = ArqSolicitacaoMOD.create()
            solicitacao.salvar_log_transicao(
                status_evento=LogSolicitacoesUsuario.INICIO_FLUXO_SOLICITACAO,
                usuario=user
            )
        except ObjectDoesNotExist as e:
            return SoapResponse(str_status='false', str_menssagem=str(e))

        except IntegrityError as e:
            return SoapResponse(str_status='false', str_menssagem=str(e))

        except Exception:
            msg = 'Houve um erro ao salvar a solicitação.'
            return SoapResponse(str_status='false', str_menssagem=msg)

        return SoapResponse(str_status='true', str_menssagem='Solicitação criada com sucesso.')

    @rpc(oWsAcessoModel, ArqCancelamento, _returns=SoapResponse) # noqa C901
    def Cancelamento(ctx, oWsAcessoModel, ArqCancelamento):

        try:
            user, token = TokenAuthentication().authenticate(oWsAcessoModel)

        except exceptions.AuthenticationFailed as e:
            return SoapResponse(str_status='false', str_menssagem=str(e))

        try:
            ArqCancelamento.cancel(user)
        except ObjectDoesNotExist as e:
            return SoapResponse(str_status='false', str_menssagem=str(e))

        except IntegrityError as e:
            return SoapResponse(str_status='false', str_menssagem=str(e))

        except EOLException as e:
            return SoapResponse(str_status='false', str_menssagem=str(e))

        except Exception:
            msg = 'Houve um erro ao receber a solicitação de cancelamento.'
            return SoapResponse(str_status='false', str_menssagem=msg)

        return SoapResponse(str_status='true', str_menssagem='Solicitação de cancelamento recebida com sucesso')


def _method_return_string(ctx):
    ctx.out_string[0] = ctx.out_string[0].replace(b'tns:', b'')
    ctx.out_string[0] = ctx.out_string[0].replace(b'soap11env', b'soap')


SolicitacaoService.event_manager.add_listener(
    'method_return_string',
    _method_return_string
)


soap_app = Application(
    [SolicitacaoService],
    tns=NS,
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

django_soap_application = DjangoApplication(soap_app)
# if API_URL:
#     django_soap_application.doc.wsdl11.build_interface_document(API_URL + '/webserver/solicitacao-remessa/')

solicitacao_application = csrf_exempt(django_soap_application)

