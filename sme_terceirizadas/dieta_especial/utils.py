from datetime import date

from rest_framework.pagination import PageNumberPagination

from sme_terceirizadas.eol_servico.utils import EOLException, EOLService
from sme_terceirizadas.perfil.models import Usuario

from ..dados_comuns.constants import TIPO_SOLICITACAO_DIETA
from ..dados_comuns.fluxo_status import DietaEspecialWorkflow
from ..escola.models import Aluno, Escola
from ..paineis_consolidados.models import SolicitacoesCODAE
from .models import LogDietasAtivasCanceladasAutomaticamente, SolicitacaoDietaEspecial


def dietas_especiais_a_terminar():
    return SolicitacaoDietaEspecial.objects.filter(
        data_termino__lt=date.today(),
        ativo=True,
        status__in=[
            DietaEspecialWorkflow.CODAE_AUTORIZADO,
            DietaEspecialWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
            DietaEspecialWorkflow.ESCOLA_SOLICITOU_INATIVACAO
        ]
    )


def termina_dietas_especiais(usuario):
    for solicitacao in dietas_especiais_a_terminar():
        if solicitacao.tipo_solicitacao == TIPO_SOLICITACAO_DIETA.get('ALTERACAO_UE'):
            solicitacao.dieta_alterada.ativo = True
            solicitacao.dieta_alterada.save()
        solicitacao.termina(usuario)


def dietas_especiais_a_iniciar():
    return SolicitacaoDietaEspecial.objects.filter(
        data_inicio__lte=date.today(),
        ativo=False,
        status__in=[
            DietaEspecialWorkflow.CODAE_AUTORIZADO,
            DietaEspecialWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
            DietaEspecialWorkflow.ESCOLA_SOLICITOU_INATIVACAO
        ]
    )


def inicia_dietas_temporarias(usuario):
    for solicitacao in dietas_especiais_a_iniciar():
        if solicitacao.tipo_solicitacao == TIPO_SOLICITACAO_DIETA.get('ALTERACAO_UE'):
            solicitacao.dieta_alterada.ativo = False
            solicitacao.dieta_alterada.save()
        solicitacao.ativo = True
        solicitacao.save()


def get_aluno_eol(codigo_eol_aluno):
    try:
        dados_do_aluno = EOLService.get_informacoes_aluno(codigo_eol_aluno)
        return dados_do_aluno
    except EOLException as e:  # noqa F841
        return {}


def aluno_pertence_a_escola_ou_esta_na_rede(cod_escola_no_eol, cod_escola_no_sigpae) -> bool:
    # Falta verificar se o aluno está na rede
    return cod_escola_no_eol == cod_escola_no_sigpae


def gerar_log_dietas_ativas_canceladas_automaticamente(dieta, dados):
    data = dict(
        dieta=dieta,
        codigo_eol_aluno=dados['codigo_eol_aluno'],
        nome_aluno=dados['nome_aluno'],
        codigo_eol_escola_origem=dados.get('codigo_eol_escola_origem'),
        nome_escola_origem=dados.get('nome_escola_origem'),
        codigo_eol_escola_destino=dados.get('codigo_eol_escola_destino'),
        nome_escola_destino=dados.get('nome_escola_destino'),
    )
    LogDietasAtivasCanceladasAutomaticamente.objects.create(**data)


def _cancelar_dieta(dieta):
    usuario_admin = Usuario.objects.get(pk=1)
    dieta.cancelar_aluno_mudou_escola(user=usuario_admin)
    dieta.ativo = False
    dieta.save()


def _cancelar_dieta_aluno_fora_da_rede(dieta):
    usuario_admin = Usuario.objects.get(pk=1)
    dieta.cancelar_aluno_nao_pertence_rede(user=usuario_admin)
    dieta.ativo = False
    dieta.save()


def cancela_dietas_ativas_automaticamente():  # noqa C901 D205 D400
    """Se um aluno trocar de escola ou não pertencer a rede
    e se tiver uma Dieta Especial Ativa, essa dieta será cancelada automaticamente.
    """
    dietas_ativas_comuns = SolicitacoesCODAE.get_autorizados_dieta_especial().filter(tipo_solicitacao_dieta='COMUM')
    for dieta in dietas_ativas_comuns:
        aluno = Aluno.objects.get(codigo_eol=dieta.codigo_eol_aluno)
        dados_do_aluno = get_aluno_eol(dieta.codigo_eol_aluno)
        solicitacao_dieta = SolicitacaoDietaEspecial.objects.filter(pk=dieta.pk).first()

        if dados_do_aluno:
            if aluno.escola:
                cod_escola_no_sigpae = aluno.escola.codigo_eol
            else:
                cod_escola_no_sigpae = None
            # Retorna True ou False
            resposta = aluno_pertence_a_escola_ou_esta_na_rede(
                cod_escola_no_eol=dados_do_aluno['cd_escola'],
                cod_escola_no_sigpae=cod_escola_no_sigpae
            )
            escola_existe_no_sigpae = Escola.objects.filter(codigo_eol=dados_do_aluno['cd_escola']).first()

            nome_escola_destino = None
            if escola_existe_no_sigpae:
                nome_escola_destino = escola_existe_no_sigpae.nome

            dados = dict(
                codigo_eol_aluno=dieta.codigo_eol_aluno,
                nome_aluno=aluno.nome,
                codigo_eol_escola_destino=dados_do_aluno['cd_escola'],
                nome_escola_destino=nome_escola_destino,
            )
            if cod_escola_no_sigpae:
                dados['nome_escola_origem'] = aluno.escola.nome
                dados['codigo_eol_escola_origem'] = aluno.escola.codigo_eol

            if not resposta:
                gerar_log_dietas_ativas_canceladas_automaticamente(solicitacao_dieta, dados)
                # Cancelar Dieta
                _cancelar_dieta(solicitacao_dieta)
        else:
            # Aluno não pertence a rede municipal.
            dados = dict(
                codigo_eol_aluno=dieta.codigo_eol_aluno,
                nome_aluno=aluno.nome,
                codigo_eol_escola_origem=aluno.escola.codigo_eol,
                nome_escola_origem=aluno.escola.nome,
            )
            gerar_log_dietas_ativas_canceladas_automaticamente(solicitacao_dieta, dados)
            _cancelar_dieta_aluno_fora_da_rede(solicitacao_dieta)


class RelatorioPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
