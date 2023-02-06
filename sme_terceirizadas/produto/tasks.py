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
def gera_xls_relatorio_produtos_homologados_async(user, nome_arquivo, data):
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        from sme_terceirizadas.produto.api.viewsets import ProdutoViewSet
        output = io.BytesIO()
        produto_viewset = ProdutoViewSet()
        produtos_agrupados = produto_viewset.get_produtos_agrupados(data)

        subtitulo = f'Total de Produtos: {len(produtos_agrupados)} | {data.get("nome_edital")}'
        build_xlsx_generico(
            output,
            queryset_serializada=produtos_agrupados,
            titulo='Relatório de Produtos Homologados',
            subtitulo=subtitulo,
            titulo_sheet='Produtos Homologados',
            titulos_colunas=['Terceirizada', 'Produto', 'Marca', 'Edital', 'Tipo', 'Cadastro', 'Homologação'],
        )
        atualiza_central_download(obj_central_download, nome_arquivo, output.read())
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
