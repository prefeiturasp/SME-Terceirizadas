import logging
from smtplib import SMTPServerDisconnected

from celery import shared_task
from rest_framework.exceptions import ValidationError

from .utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    envia_email_em_massa,
    envia_email_unico,
    gera_objeto_na_central_download
)

logger = logging.getLogger(__name__)


# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def envia_email_em_massa_task(assunto, corpo, emails, template=None, dados_template=None, html=None):
    return envia_email_em_massa(assunto, corpo, emails, template, dados_template, html)


@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def envia_email_unico_task(assunto, corpo, email, template=None, dados_template=None, html=None):
    return envia_email_unico(assunto, corpo, email, template, dados_template, html)


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
        arquivo = relatorio_geral_dieta_especial_pdf(form, queryset, user)
        atualiza_central_download(obj_central_download, nome_arquivo, arquivo)
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
