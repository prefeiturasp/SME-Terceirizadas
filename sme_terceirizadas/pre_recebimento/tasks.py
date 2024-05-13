import io
import logging
from datetime import date

import pandas as pd
from celery import shared_task
from django.contrib.auth import get_user_model

from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download,
)
from sme_terceirizadas.pre_recebimento.api.helpers import contador_relatorio_cronograma

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={"max_retries": 8},
    time_limit=3000,
    soft_time_limit=3000,
)
def gerar_relatorio_cronogramas_xlsx_async(user_id, dados, subtitulo):
    logger.info(
        "x-x-x-x Iniciando a geração do arquivo relatorio_cronogramas.xlsx x-x-x-x"
    )

    HEADERS = [
        "Nº do Cronograma",
        "Produto",
        "Empresa",
        "Marca",
        "Quantidade Total",
        "Unidade",
        "Custo Unitário",
        "Armazém",
        "Status",
        "Etapa",
        "Parte",
        "Data de Entrega",
        "Quantidade",
        "Unidade/Etapa",
        "Total de Embalagens",
        "Situação",
    ]

    ULTIMA_COLUNA = len(HEADERS) - 1

    TITULO_ARQUIVO = "relatorio_cronogramas.xlsx"
    TITULO_RELATORIO = "Relatório de Cronogramas"

    obj_central_download = gera_objeto_na_central_download(
        user=get_user_model().objects.get(id=user_id),
        identificador=TITULO_ARQUIVO,
    )

    output = io.BytesIO()
    xlsxwriter = pd.ExcelWriter(output, engine="xlsxwriter")

    try:
        if dados:
            df = pd.DataFrame(dados)
            df.insert(13, "unidade_etapa", value=df.iloc[:, 5])

        else:
            df = pd.DataFrame()

        df.to_excel(
            xlsxwriter,
            TITULO_RELATORIO,
            index=False,
            header=False,
            startrow=3,
        )
        workbook = xlsxwriter.book
        worksheet = xlsxwriter.sheets[TITULO_RELATORIO]

        _definir_largura_colunas(worksheet)
        _formatar_titulo(ULTIMA_COLUNA, TITULO_RELATORIO, workbook, worksheet)
        _formatar_subtitulo(subtitulo, ULTIMA_COLUNA, workbook, worksheet)
        _formatar_headers(HEADERS, workbook, worksheet)

        xlsxwriter.close()
        output.seek(0)

        atualiza_central_download(
            obj_central_download,
            TITULO_ARQUIVO,
            output.read(),
        )

    except Exception as e:
        atualiza_central_download_com_erro(obj_central_download, str(e))

    finally:
        logger.info(
            "x-x-x-x Finaliza a geração do arquivo relatorio_cronogramas.xlsx x-x-x-x"
        )


def _definir_largura_colunas(worksheet):
    LARGURA_COLUNAS = {
        "A:A": 18,
        "B:B": 40,
        "C:C": 30,
        "D:D": 18,
        "E:E": 18,
        "F:F": 10,
        "G:G": 25,
        "H:H": 30,
        "I:I": 20,
        "J:J": 10,
        "K:K": 10,
        "L:L": 18,
        "M:M": 12,
        "N:N": 10,
        "O:O": 12,
        "P:P": 10,
    }

    for col, width in LARGURA_COLUNAS.items():
        worksheet.set_column(col, width)


def _formatar_titulo(ULTIMA_COLUNA, TITULO_RELATORIO, workbook, worksheet):
    ALTURA_LINHA_TITULO = 65
    LINHA_TITULO = 0
    LOGO_SIGPAE = "sme_terceirizadas/static/images/logo-sigpae-light.png"

    titulo_format = workbook.add_format(
        {
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#a9d18e",
            "border_color": "#198459",
        }
    )
    worksheet.set_row(LINHA_TITULO, ALTURA_LINHA_TITULO)
    worksheet.merge_range(
        LINHA_TITULO,
        0,
        LINHA_TITULO,
        ULTIMA_COLUNA,
        TITULO_RELATORIO,
        titulo_format,
    )
    worksheet.insert_image(
        LINHA_TITULO,
        0,
        LOGO_SIGPAE,
        {"x_offset": 10, "y_offset": 10},
    )


def _formatar_subtitulo(subtitulo, ULTIMA_COLUNA, workbook, worksheet):
    ALTURA_LINHA_SUBTITULO = 50
    LINHA_SUBTITULO = 1

    subtitulo_format = workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "valign": "vcenter",
        }
    )
    worksheet.set_row(LINHA_SUBTITULO, ALTURA_LINHA_SUBTITULO)
    worksheet.merge_range(
        LINHA_SUBTITULO,
        0,
        LINHA_SUBTITULO,
        ULTIMA_COLUNA,
        subtitulo,
        subtitulo_format,
    )


def _formatar_headers(HEADERS, workbook, worksheet):
    ALTURA_LINHA_HEADERS = 30
    LINHA_HEADERS = 2

    headers_format = workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "align": "left",
            "valign": "vcenter",
            "bg_color": "#a9d18e",
        }
    )
    worksheet.set_row(LINHA_HEADERS, ALTURA_LINHA_HEADERS)
    for index, header in enumerate(HEADERS):
        worksheet.write(
            LINHA_HEADERS,
            index,
            header,
            headers_format,
        )


def subtitulo_relatorio_cronogramas(qs_cronogramas):
    result = "Total de Cronogramas Criados"
    result += f": {qs_cronogramas.count()}"

    ordered_status_count = contador_relatorio_cronograma(qs_cronogramas)
    status_count_string = "".join(
        [f" | {status}: {count}" for status, count in ordered_status_count.items()]
    )
    result += status_count_string

    result += f" | Data de Extração do Relatório: {date.today().strftime('%d/%m/%Y')}"

    return result
