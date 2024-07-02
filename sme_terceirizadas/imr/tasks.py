
import logging
from celery import shared_task
from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download,
)
from sme_terceirizadas.imr.api.services import RelatorioNotificacaoService
from sme_terceirizadas.imr.models import FormularioSupervisao
from sme_terceirizadas.relatorios.relatorios import exportar_relatorio_notificacoes

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={"max_retries": 8},
    time_limit=3000,
    soft_time_limit=3000,
)
def gerar_relatorio_notificacoes_pdf_async(user, formulario_supervisao_uuid):
    logger.info(
        "Iniciando gerar_relatorio_notificacoes_pdf_async"
    )

    formulario_supervisao = FormularioSupervisao.by_uuid(uuid=formulario_supervisao_uuid)

    TITULO_ARQUIVO = "relatorio_notificacoes.pdf"

    central_download = gera_objeto_na_central_download(
        user=user,
        identificador=TITULO_ARQUIVO,
    )

    try:
        service = RelatorioNotificacaoService(formulario_supervisao)
        dados_formatados = service.retornar_dados_formatados()
        arquivo_relatorio = exportar_relatorio_notificacoes(dados_formatados, TITULO_ARQUIVO)

        atualiza_central_download(
            central_download,
            TITULO_ARQUIVO,
            arquivo_relatorio,
        )
    except Exception as e:
        atualiza_central_download_com_erro(central_download, str(e))
    finally:
        logger.info(
            "Finaliza gerar_relatorio_notificacoes_pdf_async"
        )
