import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={"max_retries": 8},
    time_limit=3000,
    soft_time_limit=3000,
)
def gerar_pdf_protocolo_padrao_async(user, nome_arquivo, params):
    logger.info(
        "Solicitação de impressão recebida para o protocolo %s.",
        params["protocolo_uuid"],
    )
