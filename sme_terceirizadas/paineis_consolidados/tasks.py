import io
import logging

import numpy as np
from celery import shared_task

from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download
)
from sme_terceirizadas.escola.models import Escola, Lote, TipoUnidadeEscolar
from sme_terceirizadas.paineis_consolidados.api.serializers import SolicitacoesExportXLSXSerializer
from sme_terceirizadas.paineis_consolidados.models import SolicitacoesCODAE

logger = logging.getLogger(__name__)


def build_subtitulo(data, status_, queryset, lotes, tipos_solicitacao, tipos_unidade, unidades_educacionais):
    subtitulo = f'Total de Solicitações {status_}: {len(queryset)}'

    nomes_lotes = ', '.join([lote.nome for lote in Lote.objects.filter(uuid__in=lotes)])
    subtitulo += f' | Lote(s): {nomes_lotes}' if nomes_lotes else ''

    de_para_tipos_solicitacao = {
        'INC_ALIMENTA': 'Inclusão de Alimentação',
        'ALT_CARDAPIO': 'Alteração do tipo de Alimentação',
        'KIT_LANCHE_AVULSA': 'Kit Lanche',
        'INV_CARDAPIO': 'Inversão de dia de Cardápio',
        'SUSP_ALIMENTACAO': 'Suspensão de Alimentação'
    }
    nomes_tipos_solicitacao = ', '.join([de_para_tipos_solicitacao[tipo_sol] for tipo_sol in tipos_solicitacao])
    subtitulo += f' | Tipo(s) de solicitação(ões): {nomes_tipos_solicitacao}' if nomes_tipos_solicitacao else ''

    nomes_tipos_unidade = ', '.join([
        tipo_unidade.iniciais for tipo_unidade in TipoUnidadeEscolar.objects.filter(uuid__in=tipos_unidade)])
    subtitulo += f' | Tipo(s) unidade(s): {nomes_tipos_unidade}' if nomes_tipos_unidade else ''

    nomes_ues = ', '.join([
        escola.nome for escola in Escola.objects.filter(uuid__in=unidades_educacionais)])
    subtitulo += f' | Unidade(s) educacional(is): {nomes_ues}' if nomes_ues else ''

    data_inicial = data.get('de')
    subtitulo += f' | Data inicial: {data_inicial}' if data_inicial else ''

    data_final = data.get('ate')
    subtitulo += f' | Data final: {data_final}' if data_final else ''

    return subtitulo


def build_xlsx(output, serializer, queryset, data, lotes, tipos_solicitacao, tipos_unidade, unidades_educacionais):
    LINHA_0 = 0
    LINHA_1 = 1
    LINHA_2 = 2
    LINHA_3 = 3

    COLUNA_1 = 1
    COLUNA_2 = 2
    COLUNA_3 = 3
    COLUNA_4 = 4
    COLUNA_5 = 5
    COLUNA_6 = 6
    COLUNA_7 = 7

    ALTURA_COLUNA_30 = 30
    ALTURA_COLUNA_50 = 50

    import pandas as pd
    xlwriter = pd.ExcelWriter(output, engine='xlsxwriter')

    df = pd.DataFrame(serializer.data)

    # Adiciona linhas em branco no comeco do arquivo
    df_auxiliar = pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns)
    df = df_auxiliar.append(df, ignore_index=True)
    df = df_auxiliar.append(df, ignore_index=True)
    df = df_auxiliar.append(df, ignore_index=True)

    status_ = data.get('status').capitalize()
    if status_ == 'Em_andamento':
        status_ = 'Recebidas'
    else:
        status_ = list(status_)
        status_[-2] = 'a'
        status_ = ''.join(status_)

    titulo = f'Relatório de Solicitações de Alimentação {status_}'

    df.to_excel(xlwriter, f'Relatório - {status_}')
    workbook = xlwriter.book
    worksheet = xlwriter.sheets[f'Relatório - {status_}']
    worksheet.set_row(LINHA_0, ALTURA_COLUNA_50)
    worksheet.set_row(LINHA_1, ALTURA_COLUNA_30)
    worksheet.set_column('B:H', ALTURA_COLUNA_30)
    merge_format = workbook.add_format({'align': 'center', 'bg_color': '#a9d18e', 'border_color': '#198459'})
    merge_format.set_align('vcenter')
    merge_format.set_bold()
    cell_format = workbook.add_format()
    cell_format.set_text_wrap()
    cell_format.set_align('vcenter')
    cell_format.set_bold()
    v_center_format = workbook.add_format()
    v_center_format.set_align('vcenter')
    single_cell_format = workbook.add_format({'bg_color': '#a9d18e'})
    len_cols = len(df.columns)
    worksheet.merge_range(0, 0, 0, len_cols, titulo, merge_format)

    subtitulo = build_subtitulo(data, status_, queryset, lotes, tipos_solicitacao, tipos_unidade, unidades_educacionais)

    worksheet.merge_range(LINHA_1, 0, LINHA_2, len_cols, subtitulo, cell_format)
    worksheet.insert_image('A1', 'sme_terceirizadas/static/images/logo-sigpae-light.png')
    worksheet.write(LINHA_3, COLUNA_1, 'Lote', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_2, 'Unidade Educacional', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_3, 'Tipo de Solicitação', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_4, 'Data do Evento', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_5, 'Nª de Alunos', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_6, 'Observações', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_7, 'Data da Autorização', single_cell_format)

    df.reset_index(drop=True, inplace=True)
    xlwriter.save()
    output.seek(0)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_xls_relatorio_solicitacoes_alimentacao_async(user, nome_arquivo, data, uuids, lotes, tipos_solicitacao,
                                                      tipos_unidade, unidades_educacionais):
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)
    try:
        queryset = SolicitacoesCODAE.objects.filter(uuid__in=uuids)

        # remove duplicados
        aux = []
        sem_uuid_repetido = []
        for resultado in queryset:
            if resultado.uuid not in aux:
                aux.append(resultado.uuid)
                sem_uuid_repetido.append(resultado)

        status_ = data.get('status')
        serializer = SolicitacoesExportXLSXSerializer(
            sem_uuid_repetido, context={'status': status_.upper()}, many=True)

        output = io.BytesIO()

        build_xlsx(output, serializer, sem_uuid_repetido, data, lotes, tipos_solicitacao, tipos_unidade,
                   unidades_educacionais)
        atualiza_central_download(obj_central_download, nome_arquivo, output.read())
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
