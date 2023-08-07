import datetime
import logging

from celery import shared_task
from dateutil.relativedelta import relativedelta

from ..dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download
)
from ..escola.models import Escola
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
        if not SolicitacaoMedicaoInicial.objects.filter(
            escola=escola,
            ano=data_hoje.year,
            mes=f'{data_hoje.month:02d}'
        ).exists():
            try:
                solicitacao_mes_anterior = SolicitacaoMedicaoInicial.objects.get(
                    escola=escola,
                    ano=data_mes_anterior.year,
                    mes=f'{data_mes_anterior.month:02d}'
                )
                solicitacao_atual = SolicitacaoMedicaoInicial.objects.create(
                    escola=escola,
                    ano=data_hoje.year,
                    mes=f'{data_hoje.month:02d}',
                    tipo_contagem_alimentacoes=solicitacao_mes_anterior.tipo_contagem_alimentacoes,
                    criado_por=solicitacao_mes_anterior.criado_por
                )
                solicitacao_atual.save()

                for responsavel in solicitacao_mes_anterior.responsaveis.all():
                    Responsavel.objects.create(
                        solicitacao_medicao_inicial=solicitacao_atual,
                        nome=responsavel.nome,
                        rf=responsavel.rf
                    )

                solicitacao_atual.inicia_fluxo(user=solicitacao_mes_anterior.logs.first().usuario)
            except SolicitacaoMedicaoInicial.DoesNotExist:
                message = 'x-x-x-x Não existe Solicitação de Medição Inicial para a escola '
                message += f'{escola.nome} no mês anterior ({data_mes_anterior.month:02d}/{data_mes_anterior.year}) '
                message += 'x-x-x-x'
                logger.info(message)
                pass


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
