from celery import shared_task
from django.core import management
from requests import ConnectionError


# https://docs.celeryproject.org/en/latest/userguide/tasks.html


@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=5,
    retry_kwargs={'max_retries': 2},
)
def atualiza_total_alunos_escolas():
    print('entrou')
    management.call_command("atualiza_total_alunos_escolas", verbosity=0)
    return 2 + 2


@shared_task(
    retry_backoff=True,
    retry_kwargs={'max_retries': 2},
)
def teste():
    print('entrou')
    return 2 + 2
