import datetime
import logging

from celery import shared_task

from ..escola.models import EscolaPeriodoEscolar, PeriodoEscolar, TipoUnidadeEscolar
from .models import VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar

logger = logging.getLogger('sigpae.taskCardapio')


@shared_task(
    retry_backoff=5,
    retry_kwargs={'max_retries': 2},
)
def ativa_desativa_vinculos_alimentacao_com_periodo_escolar_e_tipo_unidade_escolar():
    logger.debug(f'Iniciando task ativa_desativa_vinculos_alimentacao_com_periodo_escolar_e_tipo_unidade_escolar'
                 f' às {datetime.datetime.now()}')
    for periodo_escolar in PeriodoEscolar.objects.all():
        for tipo_unidade in TipoUnidadeEscolar.objects.all():
            vinculo, created = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.get_or_create(
                tipo_unidade_escolar=tipo_unidade, periodo_escolar=periodo_escolar)
            tem_alunos_neste_periodo_e_tipo_ue = EscolaPeriodoEscolar.objects.filter(periodo_escolar=periodo_escolar,
                                                                                     escola__tipo_unidade=tipo_unidade,
                                                                                     quantidade_alunos__gte=1
                                                                                     ).exists()
            vinculo.ativo = tem_alunos_neste_periodo_e_tipo_ue
            vinculo.save()
