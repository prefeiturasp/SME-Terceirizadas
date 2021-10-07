from celery import shared_task

from sme_terceirizadas.dieta_especial.models import PlanilhaDietasAtivas
from sme_terceirizadas.escola.utils_escola import get_escolas

from ..perfil.models import Usuario
from .utils import cancela_dietas_ativas_automaticamente, inicia_dietas_temporarias, termina_dietas_especiais


# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def processa_dietas_especiais_task():
    usuario_admin = Usuario.objects.get(pk=1)
    inicia_dietas_temporarias(usuario=usuario_admin)
    termina_dietas_especiais(usuario=usuario_admin)


@shared_task
def cancela_dietas_ativas_automaticamente_task():
    cancela_dietas_ativas_automaticamente()


@shared_task
def get_escolas_task():
    obj = PlanilhaDietasAtivas.objects.first()  # Tem um problema aqui, e se selecionar outro arquivo?
    arquivo = obj.arquivo
    arquivo_unidades_da_rede = obj.arquivo_unidades_da_rede
    get_escolas(arquivo, arquivo_unidades_da_rede, obj.tempfile, in_memory=True)
