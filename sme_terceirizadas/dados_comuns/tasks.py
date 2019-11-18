from smtplib import SMTPServerDisconnected

from celery import shared_task

from .utils import envia_email_em_massa, envia_email_unico


# https://docs.celeryproject.org/en/latest/userguide/tasks.html

@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def envia_email_em_massa_task(assunto, corpo, emails, html=None):
    return envia_email_em_massa(assunto, corpo, emails, html)


@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def envia_email_unico_task(assunto, corpo, email, html=None):
    return envia_email_unico(assunto, corpo, email, html)
