import io
import logging

from celery import shared_task

from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    build_xlsx_generico,
    gera_objeto_na_central_download
)
from sme_terceirizadas.produto.models import Produto

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_xls_relatorio_produtos_homologados_async(user, nome_arquivo, data, perfil_nome, tipo_usuario, object_id):
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        from sme_terceirizadas.produto.api.viewsets import HomologacaoProdutoPainelGerencialViewSet

        agrupado_nome_marca = data.get('agrupado_por_nome_e_marca')
        output = io.BytesIO()

        hom_produto_painel_viewset = HomologacaoProdutoPainelGerencialViewSet()
        queryset = hom_produto_painel_viewset.get_queryset_solicitacoes_homologacao_por_status(
            data, perfil_nome, tipo_usuario, object_id, 'codae_homologado'
        )
        uuids = [hom_prod.uuid for hom_prod in queryset]
        qs_produtos = Produto.objects.filter(homologacao__uuid__in=uuids)
        total_marcas = qs_produtos.values_list('marca__nome', flat=True).distinct().count()
        total_produtos = len(queryset)

        if agrupado_nome_marca:
            titulos_colunas = ['Produto', 'Marca', 'Edital']
            produtos_agrupados = hom_produto_painel_viewset.produtos_agrupados_nome_marca(
                data.get('nome_edital'), qs_produtos, 0, len(queryset))
        else:
            titulos_colunas = ['Terceirizada', 'Produto', 'Marca', 'Edital', 'Tipo', 'Cadastro', 'Homologação']
            produtos_agrupados = hom_produto_painel_viewset.produtos_sem_agrupamento(
                data.get('nome_edital'), queryset, 0, len(queryset))

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
