import io
import logging
from datetime import date

import pandas as pd
from celery import shared_task
from django.contrib.auth import get_user_model

from sme_terceirizadas.dados_comuns.fluxo_status import CronogramaWorkflow
from sme_terceirizadas.dados_comuns.utils import (
    atualiza_central_download,
    atualiza_central_download_com_erro,
    gera_objeto_na_central_download,
)
from sme_terceirizadas.pre_recebimento.api.filters import CronogramaFilter
from sme_terceirizadas.pre_recebimento.api.serializers.serializers import (
    EtapaCronogramaRelatorioSerializer,
)
from sme_terceirizadas.pre_recebimento.models.cronograma import (
    Cronograma,
    EtapasDoCronograma,
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={"max_retries": 8},
    time_limit=3000,
    soft_time_limit=3000,
)
def gerar_relatorio_cronogramas_xlsx_async(user_id, filters):
    logger.info(
        "x-x-x-x Iniciando a geração do arquivo relatorio_cronogramas.xlsx x-x-x-x"
    )

    ALTURA_LINHA_TITULO = 65
    ALTURA_LINHA_SUBTITULO = 50
    ALTURA_LINHA_HEADERS = 30

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

    LINHA_TITULO = 0
    LINHA_SUBTITULO = 1
    LINHA_HEADERS = 2

    ULTIMA_COLUNA = len(HEADERS) - 1

    TITULO_ARQUIVO = "relatorio_cronogramas.xlsx"
    TITULO_RELATORIO = "Relatório de Cronogramas"

    LOGO_SIGPAE = "sme_terceirizadas/static/images/logo-sigpae-light.png"

    obj_central_download = gera_objeto_na_central_download(
        user=get_user_model().objects.get(id=user_id),
        identificador=TITULO_ARQUIVO,
    )

    cronogramas = CronogramaFilter(filters, Cronograma.objects.all()).qs
    etapas = EtapasDoCronograma.objects.filter(cronograma__in=cronogramas).order_by(
        "cronograma__numero",
        "etapa",
        "parte",
    )
    serializer = EtapaCronogramaRelatorioSerializer(etapas, many=True)

    output = io.BytesIO()
    xlsxwriter = pd.ExcelWriter(output, engine="xlsxwriter")

    try:
        if serializer.data:
            df = pd.DataFrame(serializer.data)
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

        for col, width in LARGURA_COLUNAS.items():
            worksheet.set_column(col, width)

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
            _subtitulo_relatorio_cronogramas(cronogramas, dict(**(filters or {}))),
            subtitulo_format,
        )

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


def _subtitulo_relatorio_cronogramas(qs_cronogramas, filters):
    result = "Total de Cronogramas Criados"

    if filters:
        filters.pop("status", None)
        initial_date = filters.pop("data_inicial", None)
        final_date = filters.pop("data_final", None)
        filter_map = {
            "nome_empresa": "Empresa",
            "nome_produto": "Produto",
            "numero": "Cronograma Nº",
        }
        filter_data = "".join(
            f" - {filter_map.get(k, k)} {v}" for k, v in filters.items()
        )
        filter_data += (
            f" - de {initial_date} até {final_date}"
            if initial_date and final_date
            else ""
        )

        result += filter_data

    result += f": {qs_cronogramas.count()}"

    status_list = qs_cronogramas.values_list("status", flat=True).distinct()
    status_count = "".join(
        [
            f" | {CronogramaWorkflow.states[s].title}: {qs_cronogramas.filter(status=s).count()}"
            for s in status_list
        ]
    )
    result += status_count

    result += f" | Data de Extração do Relatório: {date.today().strftime('%d/%m/%Y')}"

    return result
