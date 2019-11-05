from celery import shared_task

from .utils import envia_email_em_massa, envia_email_unico


@shared_task
def envia_email_em_massa_task(assunto, corpo, emails, html=None):
    return envia_email_em_massa(assunto, corpo, emails, html)


@shared_task
def envia_email_unico_task(assunto, corpo, email, html=None):
    return envia_email_unico(assunto, corpo, email, html)
