import logging
from pprint import pprint

from celery import shared_task
from src.dieta_especial.protocolo_padrao.models import ProtocoloPadraoDietaEspecial
from src.dieta_especial.protocolo_padrao.services.dados_protocolo_padrao import preparar_dados_protocolo_padrao

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={"max_retries": 8},
    time_limit=3000,
    soft_time_limit=3000,
)
def gerar_pdf_protocolo_padrao_async(user, nome_arquivo, params):
    protocolo = ProtocoloPadraoDietaEspecial.objects.get(
        uuid=params["protocolo_uuid"],
        ativo=True,
    )
    dados = preparar_dados_protocolo_padrao(protocolo)
    logger.info(
            "Dados do protocolo %s preparados para impressão.",
            params["protocolo_uuid"],
    )
