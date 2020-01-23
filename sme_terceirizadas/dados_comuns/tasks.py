from smtplib import SMTPServerDisconnected

from celery import shared_task

from .utils import envia_email_em_massa, envia_email_unico


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
