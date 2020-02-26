from celery import shared_task

from .utils import expira_dietas_especiais


# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def expira_dietas_especiais_task():
    return expira_dietas_especiais()
