from django.http import HttpResponse
from openpyxl import Workbook, styles
from openpyxl.worksheet.datavalidation import DataValidation

from sme_terceirizadas.imr.models import TipoGravidade
from sme_terceirizadas.terceirizada.models import Edital


def exportar_planilha_importacao_tipos_penalidade(request, **kwargs):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response[
        "Content-Disposition"
    ] = "attachment; filename=planilha_importacao_tipos_penalidade.xlsx"
    workbook: Workbook = Workbook()
    ws = workbook.active
    ws.title = "Tipos de Penalidade"
    headers = [
        "Edital",
        "Número da Cláusula/Item",
        "Gravidade",
        "Obrigações (separadas por ;)",
        "Descrição da Cláusula/Item",
        "Status",
    ]
    sheet = workbook["Tipos de Penalidade"]
    for column in "ABCDEFGF":
        sheet.column_dimensions[column].width = 30
    _font = styles.Font(name="Calibri", sz=10)
    {k: setattr(styles.DEFAULT_FONT, k, v) for k, v in _font.__dict__.items()}
    for i in range(0, len(headers)):
        cabecalho = ws.cell(row=1, column=1 + i, value=headers[i])
        cabecalho.fill = styles.PatternFill("solid", fgColor="ffff99")
        cabecalho.font = styles.Font(name="Calibri", size=10, bold=True)
        cabecalho.border = styles.Border(
            left=styles.Side(border_style="thin", color="000000"),
            right=styles.Side(border_style="thin", color="000000"),
            top=styles.Side(border_style="thin", color="000000"),
            bottom=styles.Side(border_style="thin", color="000000"),
        )

    editais = ", ".join([edital.numero for edital in Edital.objects.all()])
    dv = DataValidation(type="list", formula1='"' + editais + '"', allow_blank=True)
    dv.error = "Edital Inválido"
    dv.errorTitle = "Edital não permitido"
    ws.add_data_validation(dv)
    dv.add("A2:A1048576")

    tipos_gravidade = ", ".join(
        [gravidade.tipo for gravidade in TipoGravidade.objects.all()]
    )
    dv2 = DataValidation(
        type="list", formula1='"' + tipos_gravidade + '"', allow_blank=True
    )
    dv2.error = "Tipo de Gravidade Inválido"
    dv2.errorTitle = "Tipo de Gravidade não permitido"
    ws.add_data_validation(dv2)
    dv2.add("C2:C1048576")

    dv3 = DataValidation(type="list", formula1='"Ativo,Inativo"', allow_blank=True)
    dv3.error = "Status Inválido"
    dv3.errorTitle = "Status não permitido"
    ws.add_data_validation(dv3)
    dv3.add("F2:F1048576")

    workbook.save(response)

    return response
