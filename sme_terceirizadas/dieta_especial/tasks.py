import datetime
import logging

from celery import shared_task
from rest_framework.exceptions import ValidationError

from sme_terceirizadas.dieta_especial.models import (
    ClassificacaoDieta,
    LogQuantidadeDietasAutorizadas,
    PlanilhaDietasAtivas,
    SolicitacaoDietaEspecial
)
from sme_terceirizadas.escola.utils_escola import get_escolas

from ..dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download
)
from ..escola.models import Escola, TipoGestao
from ..perfil.models import Usuario
from ..relatorios.relatorios import relatorio_dietas_especiais_terceirizada
from .utils import cancela_dietas_ativas_automaticamente, inicia_dietas_temporarias, termina_dietas_especiais

logger = logging.getLogger(__name__)


# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def processa_dietas_especiais_task():
    usuario_admin = Usuario.objects.get(pk=1)
    inicia_dietas_temporarias(usuario=usuario_admin)
    termina_dietas_especiais(usuario=usuario_admin)


@shared_task
def cancela_dietas_ativas_automaticamente_task():
    cancela_dietas_ativas_automaticamente()


@shared_task
def get_escolas_task():
    obj = PlanilhaDietasAtivas.objects.first()  # Tem um problema aqui, e se selecionar outro arquivo?
    arquivo = obj.arquivo
    arquivo_unidades_da_rede = obj.arquivo_unidades_da_rede
    get_escolas(arquivo, arquivo_unidades_da_rede, obj.tempfile, in_memory=True)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_pdf_relatorio_dieta_especial_async(user, nome_arquivo, ids_dietas, data):
    from ..dieta_especial.forms import RelatorioDietaForm
    from ..dieta_especial.models import SolicitacaoDietaEspecial
    from ..relatorios.relatorios import relatorio_geral_dieta_especial_pdf

    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        form = RelatorioDietaForm(data)
        if not form.is_valid():
            raise ValidationError(form.errors)
        queryset = SolicitacaoDietaEspecial.objects.filter(id__in=ids_dietas)
        usuario = Usuario.objects.get(email=user)
        arquivo = relatorio_geral_dieta_especial_pdf(form, queryset, usuario)
        atualiza_central_download(obj_central_download, nome_arquivo, arquivo)
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def gera_logs_dietas_especiais_diariamente():
    logger.info(f'x-x-x-x Iniciando a geração de logs de dietas especiais autorizadas diaria x-x-x-x')
    ontem = datetime.date.today() - datetime.timedelta(days=1)
    dietas_autorizadas = SolicitacaoDietaEspecial.objects.filter(
        tipo_solicitacao__in=['COMUM', 'ALTERACAO_UE', 'ALUNO_NAO_MATRICULADO'],
        status__in=[
            SolicitacaoDietaEspecial.workflow_class.CODAE_AUTORIZADO,
            SolicitacaoDietaEspecial.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA,
            SolicitacaoDietaEspecial.workflow_class.ESCOLA_SOLICITOU_INATIVACAO]
    )
    terc_total = TipoGestao.objects.get(nome='TERC TOTAL')
    logs_a_criar = []
    for escola in Escola.objects.filter(tipo_gestao=terc_total):
        logger.info(f'x-x-x-x Logs para a escola {escola.nome} x-x-x-x')
        for classificacao in ClassificacaoDieta.objects.all():
            quantidade_dietas = dietas_autorizadas.filter(classificacao=classificacao, escola_destino=escola).count()
            log = LogQuantidadeDietasAutorizadas(
                quantidade=quantidade_dietas,
                escola=escola,
                data=ontem,
                classificacao=classificacao
            )
            logs_a_criar.append(log)
    LogQuantidadeDietasAutorizadas.objects.bulk_create(logs_a_criar)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_pdf_relatorio_dietas_especiais_terceirizadas_async(user, nome_arquivo, ids_dietas, data, filtros):
    from sme_terceirizadas.dieta_especial.models import SolicitacaoDietaEspecial

    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        query_set = SolicitacaoDietaEspecial.objects.filter(id__in=ids_dietas)
        usuario = Usuario.objects.get(username=user)
        solicitacoes = []
        for solicitacao in query_set:
            classificacao = solicitacao.classificacao.nome if solicitacao.classificacao else '--'
            dados_solicitacoes = {
                'codigo_eol_aluno': solicitacao.aluno.codigo_eol,
                'nome_aluno': solicitacao.aluno.nome,
                'nome_escola': solicitacao.escola.nome,
                'classificacao': classificacao,
                'protocolo_padrao': solicitacao.nome_protocolo,
                'alergias_intolerancias': solicitacao.alergias_intolerancias
            }
            if data.get('status_selecionado') == 'CANCELADAS':
                dados_solicitacoes['data_cancelamento'] = solicitacao.data_ultimo_log
            solicitacoes.append(dados_solicitacoes)
        exibir_diagnostico = usuario.tipo_usuario != 'terceirizada'
        dados = {
            'usuario_nome': usuario.nome,
            'status': data.get('status_selecionado').lower(),
            'filtros': filtros,
            'solicitacoes': solicitacoes,
            'quantidade_solicitacoes': query_set.count(),
            'diagnostico': exibir_diagnostico
        }
        arquivo = relatorio_dietas_especiais_terceirizada(dados=dados)
        atualiza_central_download(obj_central_download, nome_arquivo, arquivo)
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
