from celery import shared_task

from .utils import envia_email_em_massa, envia_email_unico


@shared_task(default_retry_delay=30, max_retries=5)  # 30s
def envia_email_em_massa_task(assunto, corpo, emails, html=None):
    return envia_email_em_massa(assunto, corpo, emails, html)


@shared_task(default_retry_delay=30, max_retries=5)  # 30s
def envia_email_unico_task(assunto, corpo, email, html=None):
    return envia_email_unico(assunto, corpo, email, html)
