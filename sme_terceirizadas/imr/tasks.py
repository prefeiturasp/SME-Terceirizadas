import logging

from celery import shared_task

from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download,
)
from sme_terceirizadas.imr.api.services import RelatorioNotificacaoService
from sme_terceirizadas.imr.models import FormularioSupervisao
from sme_terceirizadas.relatorios.relatorios import relatorio_formulario_supervisao
from sme_terceirizadas.relatorios.relatorios import exportar_relatorio_notificacoes

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={"max_retries": 8},
    time_limit=3000,
    soft_time_limit=3000,
)
def gera_pdf_relatorio_formulario_supervisao_async(user, nome_arquivo, uuid):
    solicitacao = FormularioSupervisao.objects.get(uuid=uuid)
    logger.info(f"x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x")
    obj_central_download = gera_objeto_na_central_download(
        user=user, identificador=nome_arquivo
    )
    try:
        arquivo = relatorio_formulario_supervisao(solicitacao)
        atualiza_central_download(obj_central_download, nome_arquivo, arquivo)
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))
        logger.error(f"Erro: {e}")

    logger.info(f"x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x")


@shared_task(
    retry_backoff=2,
    retry_kwargs={"max_retries": 8},
    time_limit=3000,
    soft_time_limit=3000,
)
def gerar_relatorio_notificacoes_pdf_async(user, formulario_supervisao_uuid, nome_arquivo):
    logger.info(
        "Iniciando gerar_relatorio_notificacoes_pdf_async"
    )

    formulario_supervisao = FormularioSupervisao.by_uuid(uuid=formulario_supervisao_uuid)

    central_download = gera_objeto_na_central_download(
        user=user,
        identificador=nome_arquivo,
    )

    try:
        service = RelatorioNotificacaoService(formulario_supervisao)
        dados_formatados = service.retornar_dados_formatados()
        arquivo_relatorio = exportar_relatorio_notificacoes(dados_formatados, nome_arquivo)

        atualiza_central_download(
            central_download,
            nome_arquivo,
            arquivo_relatorio,
        )
    except Exception as e:
        atualiza_central_download_com_erro(central_download, str(e))
    finally:
        logger.info(
            "Finaliza gerar_relatorio_notificacoes_pdf_async"
        )
