import io
import datetime
import logging

from celery import shared_task
from django.db.models import Q

from ..escola.constants import (
    PERIODOS_ESPECIAIS_CEI_CEU_CCI,
    PERIODOS_ESPECIAIS_CEI_DIRET,
)
from ..escola.models import (
    AlunosMatriculadosPeriodoEscola,
    EscolaPeriodoEscolar,
    PeriodoEscolar,
    TipoUnidadeEscolar,
)
from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    build_xlsx_generico,
    gera_objeto_na_central_download
)

from .api.serializers.serializers import serialize_relatorio_controle_restos, serialize_relatorio_controle_sobras
from ..escola.constants import PERIODOS_ESPECIAIS_CEI_CEU_CCI, PERIODOS_ESPECIAIS_CEI_DIRET
from ..escola.models import AlunosMatriculadosPeriodoEscola, EscolaPeriodoEscolar, PeriodoEscolar, TipoUnidadeEscolar
from .models import VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar

logger = logging.getLogger("sigpae.taskCardapio")


def bypass_ativa_vinculos(tipo_unidade, periodos_escolares):
    vinculo_tipo_unidade = (
        VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.filter(
            tipo_unidade_escolar=tipo_unidade
        )
    )
    vinculo_tipo_unidade.filter(periodo_escolar__nome__in=periodos_escolares).update(
        ativo=True
    )
    vinculo_tipo_unidade.filter(
        ~Q(periodo_escolar__nome__in=periodos_escolares)
    ).update(ativo=False)


@shared_task(
    retry_backoff=5,
    retry_kwargs={"max_retries": 2},
)
def ativa_desativa_vinculos_alimentacao_com_periodo_escolar_e_tipo_unidade_escolar():
    """O sistema assume que todas as escolas tem todos os períodos.

    Essa função ativa/desativa dinamicamente o vínculo entre TipoUE e Períodos escolares
    caso tenha ou não algum aluno em algum periodo escolar.

    OBS: período PARCIAL funciona somente para CEI CEU, CEI e CCI, para mais detalhes,
    vide `tem_somente_integral_e_parcial()` em TipoUnidadeEscolar
    """
    logger.debug(
        "Iniciando task ativa_desativa_vinculos_alimentacao_com_periodo_escolar_e_tipo_unidade_escolar"
        f" às {datetime.datetime.now()}"
    )

    # SGP não tem informações de CEU GESTAO, estamos colocando manualmente até o momento 22/07/2022
    for tipo_unidade in TipoUnidadeEscolar.objects.all().exclude(iniciais="CEU GESTAO"):
        # atualiza com base nos dados da api do EOL
        for periodo_escolar in PeriodoEscolar.objects.all():
            (
                vinculo,
                created,
            ) = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.get_or_create(
                tipo_unidade_escolar=tipo_unidade, periodo_escolar=periodo_escolar
            )
            tem_alunos_neste_periodo_e_tipo_ue = EscolaPeriodoEscolar.objects.filter(
                periodo_escolar=periodo_escolar,
                escola__tipo_unidade=tipo_unidade,
                quantidade_alunos__gte=1,
            ).exists()
            vinculo.ativo = tem_alunos_neste_periodo_e_tipo_ue
            vinculo.save()
            if tipo_unidade.iniciais in ["EMEF P FOM", "EMEI P FOM"]:
                tem_alunos_neste_periodo_e_eh_p_fom = (
                    AlunosMatriculadosPeriodoEscola.objects.filter(
                        periodo_escolar=periodo_escolar,
                        escola__tipo_unidade__iniciais=tipo_unidade,
                        tipo_turma="REGULAR",
                    ).exists()
                )
                vinculo.ativo = tem_alunos_neste_periodo_e_eh_p_fom
                vinculo.save()

        if tipo_unidade.tem_somente_integral_e_parcial:
            # deve ter periodo INTEGRAL E PARCIAL somente
            periodos_escolares = PERIODOS_ESPECIAIS_CEI_CEU_CCI
            bypass_ativa_vinculos(tipo_unidade, periodos_escolares)
        if tipo_unidade.eh_cei:
            # deve ativar INTEGRAL, MANHA E TARDE PARA CEIS DA PROPERTY CRIADA
            periodos_escolares = PERIODOS_ESPECIAIS_CEI_DIRET
            bypass_ativa_vinculos(tipo_unidade, periodos_escolares)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_xls_relatorio_controle_restos_async(user, nome_arquivo, data):
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        output = io.BytesIO()

        titulos_colunas = ['DRE', 'Unidade Educacional', 'Data da Medição', 
            'Quantidade Distribuída', 'Peso do Resto (Kg)', 'Nº Refeições', 
            'Resto per Capita', '% Resto']
        build_xlsx_generico(
            output,
            queryset_serializada=[serialize_relatorio_controle_restos(item) for item in data],
            titulo='Relatório de Controle de Restos',
            titulo_sheet=f'Relatório',
            titulos_colunas=titulos_colunas,
        )

        atualiza_central_download(obj_central_download, nome_arquivo, output.read())
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_xls_relatorio_controle_sobras_async(user, nome_arquivo, data):
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        output = io.BytesIO()

        titulos_colunas = ['DRE', 'Unidade Educacional', 'Tipo de Alimentação', 'Tipo de Alimento'
            'Data da Medição', 'Peso da Refeição Distribuída (Kg)', 'Peso da Sobra (Kg)', 
            'Total de Alunos (frequência)', 'Total Primeira Oferta', 'Total Segunda Oferta (Repetição)',
            '% Sobra', 'Média por Aluno', 'Média por Refeição']
        build_xlsx_generico(
            output,
            queryset_serializada=[serialize_relatorio_controle_sobras(item) for item in data],
            titulo='Relatório de Controle de Sobras',
            titulo_sheet=f'Relatório',
            titulos_colunas=titulos_colunas,
        )

        atualiza_central_download(obj_central_download, nome_arquivo, output.read())
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')