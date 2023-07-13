import datetime
import io
import logging

import numpy as np
from celery import shared_task
from django.template.loader import render_to_string

from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download
)
from sme_terceirizadas.escola.models import Escola, Lote, TipoUnidadeEscolar
from sme_terceirizadas.paineis_consolidados.api.serializers import SolicitacoesExportXLSXSerializer
from sme_terceirizadas.paineis_consolidados.models import MoldeConsolidado, SolicitacoesCODAE

from ..relatorios.utils import html_to_pdf_file

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

    subtitulo += f' | Data de Extração do Relatório: {datetime.date.today().strftime("%d/%m/%Y")}'

    return subtitulo


def build_xlsx(output, serializer, queryset, data, lotes, tipos_solicitacao, tipos_unidade, unidades_educacionais):
    LINHA_0 = 0
    LINHA_1 = 1
    LINHA_2 = 2
    LINHA_3 = 3

    COLUNA_0 = 0
    COLUNA_1 = 1
    COLUNA_2 = 2
    COLUNA_3 = 3
    COLUNA_4 = 4
    COLUNA_5 = 5
    COLUNA_6 = 6
    COLUNA_7 = 7
    COLUNA_8 = 8
    COLUNA_9 = 9
    COLUNA_10 = 10
    COLUNA_11 = 11

    ALTURA_COLUNA_30 = 30
    ALTURA_COLUNA_50 = 50

    import pandas as pd
    xlwriter = pd.ExcelWriter(output, engine='xlsxwriter')

    df = pd.DataFrame(serializer.data)

    novas_colunas = ['dia_semana', 'periodo_inclusao', 'tipo_alimentacao']
    for i, nova_coluna in enumerate(novas_colunas):
        df.insert(5 + i, nova_coluna, '-')

    novas_linhas, lista_uuids = [], []
    for index, solicitacao in enumerate(queryset):
        model_obj = solicitacao.get_raw_model.objects.get(uuid=solicitacao.uuid)

        if solicitacao.tipo_doc == 'INC_ALIMENTA_CONTINUA':
            for qt_periodo in model_obj.quantidades_periodo.all():
                nova_linha = df.iloc[index].copy()
                data_inicial = model_obj.data_inicial.strftime('%d/%m/%Y')
                data_final = model_obj.data_final.strftime('%d/%m/%Y')
                nova_linha['data_evento'] = f'{data_inicial} - {data_final}'
                nova_linha['dia_semana'] = qt_periodo.dias_semana_display()
                nova_linha['periodo_inclusao'] = qt_periodo.periodo_escolar.nome
                if qt_periodo.cancelado == True:
                    nova_linha['observacoes'] = qt_periodo.cancelado_justificativa
                tipos_alimentacao = ''
                for tipo in qt_periodo.tipos_alimentacao.all():
                    tipos_alimentacao = ''.join(tipo.nome)
                nova_linha['tipo_alimentacao'] = tipos_alimentacao
                nova_linha['numero_alunos'] = qt_periodo.numero_alunos
                novas_linhas.append(nova_linha)
                lista_uuids.append(solicitacao)
        else:
            linha = df.iloc[index].copy()
            novas_linhas.append(linha)
            lista_uuids.append(solicitacao)

    df = pd.DataFrame(novas_linhas)
    df.reset_index(drop=True, inplace=True)

    df.insert(0, 'N', range(1, len(df) + 1))
    df_auxiliar = pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns)
    df = df_auxiliar.append(df, ignore_index=True)
    df = df_auxiliar.append(df, ignore_index=True)
    df = df_auxiliar.append(df, ignore_index=True)

    df['N'] = df['N'].apply(lambda x: str(int(x)) if pd.notnull(x) else '')
    df['numero_alunos'] = df['numero_alunos'].astype(str)

    status_ = data.get('status').capitalize()
    if status_ == 'Em_andamento':
        status_ = 'Recebidas'
    else:
        status_ = list(status_)
        status_[-2] = 'a'
        status_ = ''.join(status_)

    titulo = f'Relatório de Solicitações de Alimentação {status_}'

    df.to_excel(xlwriter, f'Relatório - {status_}', index=False)
    workbook = xlwriter.book
    worksheet = xlwriter.sheets[f'Relatório - {status_}']
    worksheet.set_row(LINHA_0, ALTURA_COLUNA_50)
    worksheet.set_row(LINHA_1, ALTURA_COLUNA_30)
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 8)
    worksheet.set_column('C:C', 40)
    worksheet.set_column('D:D', 30)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:G', 30)
    worksheet.set_column('H:H', 10)
    worksheet.set_column('I:I', 30)
    worksheet.set_column('J:J', 13)
    worksheet.set_column('K:K', 30)
    worksheet.set_column('L:L', 20)
    merge_format = workbook.add_format({'align': 'center', 'bg_color': '#a9d18e', 'border_color': '#198459'})
    merge_format.set_align('vcenter')
    merge_format.set_bold()
    cell_format = workbook.add_format()
    cell_format.set_text_wrap()
    cell_format.set_align('vcenter')
    cell_format.set_bold()
    single_cell_format = workbook.add_format({'bg_color': '#a9d18e'})
    len_cols = len(df.columns) - 1
    worksheet.merge_range(0, 0, 0, len_cols, titulo, merge_format)

    subtitulo = build_subtitulo(data, status_, queryset, lotes, tipos_solicitacao, tipos_unidade, unidades_educacionais)

    worksheet.merge_range(LINHA_1, 0, LINHA_2, len_cols, subtitulo, cell_format)
    worksheet.insert_image('A1', 'sme_terceirizadas/static/images/logo-sigpae-light.png')
    worksheet.write(LINHA_3, COLUNA_0, 'N', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_1, 'Lote', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_2, 'Terceirizada' if status_ == 'Recebidas' else 'Unidade Educacional',
                    single_cell_format)
    worksheet.write(LINHA_3, COLUNA_3, 'Tipo de Solicitação', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_4, 'ID da Solicitação', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_5, 'Data do Evento', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_6, 'Dia da semana', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_7, 'Período', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_8, 'Tipo de Alimentação', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_9, 'Nª de Alunos', single_cell_format)
    worksheet.write(LINHA_3, COLUNA_10, 'Observações', single_cell_format)
    map_data = {
        'Autorizadas': 'Data de Autorização',
        'Canceladas': 'Data de Cancelamento',
        'Negadas': 'Data de Negação',
        'Recebidas': 'Data de Autorização'
    }
    worksheet.write(LINHA_3, COLUNA_11, map_data[status_], single_cell_format)
    df.reset_index(drop=True, inplace=True)

    previous_solicitacao = None
    idx = 0
    for index, solicitacao in enumerate(lista_uuids):
        model_obj = solicitacao.get_raw_model.objects.get(uuid=solicitacao.uuid)

        if previous_solicitacao != solicitacao:
            idx = 0
            previous_solicitacao = solicitacao

        if solicitacao.tipo_doc in ['INC_ALIMENTA_CEMEI', 'INC_ALIMENTA_CEI', 'INC_ALIMENTA']:
            if model_obj.existe_dia_cancelado or model_obj.status == 'ESCOLA_CANCELOU':
                worksheet.write(
                    LINHA_3 + 1 + index,
                    COLUNA_5,
                    df.values[LINHA_3 + index][COLUNA_5],
                    workbook.add_format({'align': 'left', 'bg_color': 'yellow'})
                )
        if solicitacao.tipo_doc == 'INC_ALIMENTA_CONTINUA':
            qts_periodos = model_obj.quantidades_periodo.all()
            if idx < len(qts_periodos):
                qt_periodo = qts_periodos[idx]
                if qt_periodo.cancelado:
                    worksheet.write(
                        LINHA_3 + 1 + index,
                        COLUNA_10,
                        df.values[LINHA_3 + index][COLUNA_10],
                        workbook.add_format({'align': 'left', 'bg_color': 'yellow'})
                    )
                idx += 1

    xlwriter.save()
    output.seek(0)


def build_pdf(lista_solicitacoes_dict, status):
    html_string = render_to_string(
        'relatorio_solicitacoes_alimentacao.html',
        {'solicitacoes': lista_solicitacoes_dict,
         'total_solicitacoes': len(lista_solicitacoes_dict),
         'data_extracao_relatorio': datetime.date.today().strftime('%d/%m/%Y'),
         'status': status,
         'status_formatado': ''.join(letra for letra in status.title() if not letra.isspace())}
    )
    return html_to_pdf_file(html_string, 'relatorio_solicitacoes_alimentacao.pdf', True)


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
        queryset = SolicitacoesCODAE.objects.filter(uuid__in=uuids).order_by(
            'lote_nome', 'escola_nome', 'terceirizada_nome')

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


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=3000,
    soft_time_limit=3000
)
def gera_pdf_relatorio_solicitacoes_alimentacao_async(user, nome_arquivo, data, uuids, status):
    logger.info(f'x-x-x-x Iniciando a geração do arquivo {nome_arquivo} x-x-x-x')
    obj_central_download = gera_objeto_na_central_download(user=user, identificador=nome_arquivo)

    label_data = {
        'AUTORIZADOS': ' de Autorização',
        'CANCELADOS': ' de Cancelamento',
        'NEGADOS': ' de Negação',
        'RECEBIDAS': ' de Autorização'
    }
    property_data = {
        'AUTORIZADOS': 'data_autorizacao',
        'CANCELADOS': 'data_cancelamento',
        'NEGADOS': 'data_negacao',
        'RECEBIDAS': 'data_autorizacao'
    }

    try:
        solicitacoes = SolicitacoesCODAE.objects.filter(uuid__in=uuids)
        solicitacoes = solicitacoes.order_by('lote_nome', 'escola_nome', 'terceirizada_nome')
        solicitacoes = list(solicitacoes.values('tipo_doc', 'uuid').distinct())
        lista_solicitacoes_dict = []
        for solicitacao in solicitacoes:
            class_name = MoldeConsolidado.get_class_name(solicitacao['tipo_doc'])
            _solicitacao = class_name.objects.get(uuid=solicitacao['uuid'])
            lista_solicitacoes_dict.append(_solicitacao.solicitacao_dict_para_relatorio(
                label_data[status],
                getattr(_solicitacao, property_data[status])
            ))

        arquivo = build_pdf(lista_solicitacoes_dict, status)
        atualiza_central_download(obj_central_download, nome_arquivo, arquivo)
    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    logger.info(f'x-x-x-x Finaliza a geração do arquivo {nome_arquivo} x-x-x-x')
