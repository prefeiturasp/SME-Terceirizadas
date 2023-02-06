import io
import logging

from celery import shared_task

from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    build_xlsx_generico,
    gera_objeto_na_central_download
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_xls_relatorio_produtos_homologados_async(user, nome_arquivo, array_produtos, subtitulo):
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:

        output = io.BytesIO()
        build_xlsx_generico(
            output,
            queryset_serializada=array_produtos,
            titulo='Relatório de Produtos Homologados',
            subtitulo=subtitulo,
            titulo_sheet='Produtos Homologados',
            titulos_colunas=['Terceirizada', 'Produto', 'Marca', 'Edital', 'Tipo', 'Cadastro', 'Homologação'],
        )
        atualiza_central_download(obj_central_download, nome_arquivo, output.read())
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
