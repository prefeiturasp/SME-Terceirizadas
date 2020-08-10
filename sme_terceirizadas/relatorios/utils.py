import math

from django.http import HttpResponse
from django_weasyprint.utils import django_url_fetcher
from weasyprint import HTML

from ..dados_comuns.models import LogSolicitacoesUsuario


def formata_logs(logs):
    if logs.filter(status_evento__in=[
        LogSolicitacoesUsuario.CODAE_AUTORIZOU,
        LogSolicitacoesUsuario.CODAE_NEGOU]
    ).exists():
        logs = logs.exclude(status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU)
    return logs.exclude(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO)


def get_width(fluxo, logs):
    fluxo_utilizado = formata_logs(logs) if len(logs) > len(formata_logs(logs)) else logs
    if not fluxo_utilizado:
        return str(55) + '%'
    return str(math.floor(99 / len(fluxo_utilizado))) + '%'


def get_diretorias_regionais(lotes):
    diretorias_regionais = []
    for lote in lotes:
        if lote.diretoria_regional not in diretorias_regionais:
            diretorias_regionais.append(lote.diretoria_regional)
    return diretorias_regionais


def html_to_pdf_response(html_string, pdf_filename):
    pdf_file = HTML(
        string=html_string,
        url_fetcher=django_url_fetcher,
        base_url='file://abobrinha').write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{pdf_filename}"'
    return response
