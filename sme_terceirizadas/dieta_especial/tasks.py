import logging

from celery import shared_task
from rest_framework.exceptions import ValidationError

from sme_terceirizadas.dieta_especial.models import PlanilhaDietasAtivas
from sme_terceirizadas.escola.utils_escola import get_escolas

from ..dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download
)
from ..perfil.models import Usuario
from .utils import cancela_dietas_ativas_automaticamente, inicia_dietas_temporarias, termina_dietas_especiais

logger = logging.getLogger(__name__)


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
        usuario = Usuario.objects.get(email=user)
        arquivo = relatorio_geral_dieta_especial_pdf(form, queryset, usuario)
        atualiza_central_download(obj_central_download, nome_arquivo, arquivo)
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
