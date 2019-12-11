import datetime
import logging

from celery import shared_task
from django.core import management
from requests import ConnectionError

# https://docs.celeryproject.org/en/latest/userguide/tasks.html
logger = logging.getLogger('sigpae.taskEscola')


@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=5,
    retry_kwargs={'max_retries': 2},
)
def atualiza_total_alunos_escolas():
    logger.debug(f'Iniciando task atualiza_total_alunos_escolas às {datetime.datetime.now()}')
    management.call_command('atualiza_total_alunos_escolas', verbosity=0)


@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=5,
    retry_kwargs={'max_retries': 2},
)
def atualiza_dados_escolas():
    logger.debug(f'Iniciando task atualiza_dados_escolas às {datetime.datetime.now()}')
    management.call_command('atualiza_dados_escolas', verbosity=0)
