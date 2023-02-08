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
        agrupado_nome_marca = data.get('agrupado_por_nome_e_marca')
        output = io.BytesIO()
        produto_viewset = ProdutoViewSet()

        if agrupado_nome_marca:
            produtos_agrupados, total_produtos, total_marcas = produto_viewset.get_queryset_filtrado_agrupado(data)
            titulos_colunas = ['Produto', 'Marca', 'Edital']
        else:
            produtos_agrupados, total_produtos, total_marcas = produto_viewset.get_produtos_agrupados(data)
            titulos_colunas = ['Terceirizada', 'Produto', 'Marca', 'Edital', 'Tipo', 'Cadastro', 'Homologação']
        subtitulo = f'Total de Produtos: {total_produtos} | Total de Marcas: {total_marcas} | {data.get("nome_edital")}'
        build_xlsx_generico(
            output,
            queryset_serializada=produtos_agrupados,
            titulo=f'Relatório de Produtos Homologados{" por Nome e Marca" if agrupado_nome_marca else ""}',
            subtitulo=subtitulo,
            titulo_sheet=f'{"Visão Agrupada" if agrupado_nome_marca else "Produtos Homologados"}',
            titulos_colunas=titulos_colunas,
        )
        atualiza_central_download(obj_central_download, nome_arquivo, output.read())
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
