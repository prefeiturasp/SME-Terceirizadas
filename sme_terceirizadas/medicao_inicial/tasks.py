import datetime
import logging

from celery import shared_task
from dateutil.relativedelta import relativedelta

from ..dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download
)
from ..escola.models import AlunoPeriodoParcial, Escola
from .models import Responsavel, SolicitacaoMedicaoInicial

logger = logging.getLogger(__name__)


# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def cria_solicitacao_medicao_inicial_mes_atual():
    data_hoje = datetime.date.today()
    data_mes_anterior = data_hoje + relativedelta(months=-1)

    for escola in Escola.objects.all():
        if not solicitacao_medicao_atual_existe(escola, data_hoje):
            try:
                solicitacao_mes_anterior = buscar_solicitacao_mes_anterior(escola, data_mes_anterior)
                solicitacao_atual = criar_nova_solicitacao(solicitacao_mes_anterior, escola, data_hoje)
                copiar_responsaveis(solicitacao_mes_anterior, solicitacao_atual)

                if solicitacao_atual.ue_possui_alunos_periodo_parcial:
                    copiar_alunos_periodo_parcial(solicitacao_mes_anterior, solicitacao_atual)

                solicitacao_atual.inicia_fluxo(user=solicitacao_mes_anterior.logs.first().usuario)

            except SolicitacaoMedicaoInicial.DoesNotExist:
                message = (f'x-x-x-x Não existe Solicitação de Medição Inicial para a escola '
                           f'{escola.nome} no mês anterior ({data_mes_anterior.month:02d}/'
                           f'{data_mes_anterior.year}) x-x-x-x')
                logger.info(message)


def solicitacao_medicao_atual_existe(escola, data):
    return SolicitacaoMedicaoInicial.objects.filter(
        escola=escola,
        ano=data.year,
        mes=f'{data.month:02d}'
    ).exists()


def buscar_solicitacao_mes_anterior(escola, data):
    return SolicitacaoMedicaoInicial.objects.get(
        escola=escola,
        ano=data.year,
        mes=f'{data.month:02d}'
    )


def criar_nova_solicitacao(solicitacao_anterior, escola, data_hoje):
    attrs = {
        'escola': escola,
        'ano': data_hoje.year,
        'mes': f'{data_hoje.month:02d}',
        'criado_por': solicitacao_anterior.criado_por
    }

    if not solicitacao_anterior.escola.eh_cei:
        attrs['tipo_contagem_alimentacoes'] = solicitacao_anterior.tipo_contagem_alimentacoes
    else:
        attrs['ue_possui_alunos_periodo_parcial'] = solicitacao_anterior.ue_possui_alunos_periodo_parcial

    return SolicitacaoMedicaoInicial.objects.create(**attrs)


def copiar_responsaveis(solicitacao_origem, solicitacao_destino):
    for responsavel in solicitacao_origem.responsaveis.all():
        Responsavel.objects.create(
            solicitacao_medicao_inicial=solicitacao_destino,
            nome=responsavel.nome,
            rf=responsavel.rf
        )


def copiar_alunos_periodo_parcial(solicitacao_origem, solicitacao_destino):
    alunos_em_periodo_parcial = solicitacao_origem.alunos_periodo_parcial.all()
    for aluno in alunos_em_periodo_parcial:
        AlunoPeriodoParcial.objects.create(
            solicitacao_medicao_inicial=solicitacao_destino,
            aluno=aluno.aluno,
            escola=solicitacao_destino.escola
        )


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_pdf_relatorio_solicitacao_medicao_por_escola_async(user, nome_arquivo, uuid_sol_medicao):
    from ..medicao_inicial.models import SolicitacaoMedicaoInicial
    from ..relatorios.relatorios import relatorio_solicitacao_medicao_por_escola

    solicitacao = SolicitacaoMedicaoInicial.objects.get(uuid=uuid_sol_medicao)
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        arquivo = relatorio_solicitacao_medicao_por_escola(solicitacao)
        atualiza_central_download(obj_central_download, nome_arquivo, arquivo)
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
