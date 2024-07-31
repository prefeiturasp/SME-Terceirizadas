import io
import logging

from celery import shared_task
from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    build_xlsx_generico,
    gera_objeto_na_central_download
)
from .api.serializers.serializers import serialize_relatorio_controle_restos, serialize_relatorio_controle_sobras

logger = logging.getLogger("sigpae.taskCardapio")


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

        titulos_colunas = [
            'DRE', 'Unidade Educacional', 'Data da Medição', 'Período'
            'Cardápio', 'Tipo de Alimentação', 'Resto Predominante', 
            'Quantidade Distribuída', 'Tipo de ALimento', 'Peso do Resto (Kg)', 
            'Nº Refeições', 'Resto per Capita', '% Resto', 'Classificação'
            'Aceitabilidade', 'Observações']
        build_xlsx_generico(
            output,
            queryset_serializada=[serialize_relatorio_controle_restos(item) for item in data],
            titulo='Relatório de Controle de Restos',
            titulo_sheet='Relatório',
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

        titulos_colunas = [
            'DRE', 'Unidade Educacional', 'Tipo de Alimentação', 'Tipo de Alimento',
            'Data da Medição', 'Período', 
            'Tipo de Recipiente', 'Peso do Recipiente',
            'Peso do Alimento Pronto (Kg)', 'Peso da Sobra (Kg)', 'Peso da Refeição Distribuída (Kg)',
            'Total de Alunos (frequência)', 'Total Primeira Oferta', 'Total Segunda Oferta (Repetição)',
            '% Sobra', 'Média por Aluno', 'Média por Refeição', 'Classificação']
        build_xlsx_generico(
            output,
            queryset_serializada=[serialize_relatorio_controle_sobras(item) for item in data],
            titulo='Relatório de Controle de Sobras',
            titulo_sheet='Relatório',
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
def gera_xls_relatorio_controle_sobras_bruto_async(user, nome_arquivo, data):
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        output = io.BytesIO()

        titulos_colunas = [
            'DRE', 'Unidade Educacional', 'Data da Medição', 'Período', 
            'Tipo de Alimentação', 'Tipo de Alimento', 'Especificar Alimento',
            'Tipo de Recipiente', 'Peso do Recipiente',
            'Peso do Alimento Pronto com Recipiente', 'Peso da Sobra com Recipiente',
            'Peso do Alimento Pronto (Kg)', 'Peso da Sobra (Kg)', 'Peso da Refeição Distribuída (Kg)',
            'Total de Alunos (frequência)', 'Total Primeira Oferta', 'Total Segunda Oferta (Repetição)',
            '% Sobra', 'Média por Aluno', 'Média por Refeição', 'Classificação']
        build_xlsx_generico(
            output,
            queryset_serializada=[serialize_relatorio_controle_sobras(item) for item in data],
            titulo='Relatório de Controle de Sobras - Bruto',
            titulo_sheet='Relatório',
            titulos_colunas=titulos_colunas,
        )

        atualiza_central_download(obj_central_download, nome_arquivo, output.read())
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')