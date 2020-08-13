import math
from datetime import date

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


def get_config_cabecario_relatorio_analise(filtros, data_incial_analise_padrao, contatos_terceirizada):  # noqa C901

    tipos_cabecario = (
        'CABECARIO_POR_DATA',
        'CABECARIO_POR_NOME_TERCEIRIZADA',
        'CABECARIO_REDUZIDO')

    config = {
        'cabecario_tipo': None,
        'nome_terceirizada': None,
        'email_terceirizada': None,
        'telefone_terceirizada': None,
        'data_analise_inicial': None,
        'data_analise_final': None
    }

    if len(filtros) > 2 or len(filtros) == 0:
        config['cabecario_tipo'] = tipos_cabecario[2]
    else:
        nome_terceirizada = filtros.pop('nome_terceirizada', None)
        if nome_terceirizada and len(filtros) == 0:
            config['cabecario_tipo'] = tipos_cabecario[1]
            config['nome_terceirizada'] = nome_terceirizada
            config['email_terceirizada'] = contatos_terceirizada[0]['email']
            config['telefone_terceirizada'] = contatos_terceirizada[0]['telefone']
        elif nome_terceirizada and len(filtros) > 0:
            config['cabecario_tipo'] = tipos_cabecario[2]
        else:
            data_analise_inicial = filtros.pop('data_analise_inicial', None)
            data_analise_final = filtros.pop('data_analise_final', None)

            if data_analise_inicial or data_analise_final:
                config['cabecario_tipo'] = tipos_cabecario[0]
                if not data_analise_inicial:
                    data_analise_inicial = data_incial_analise_padrao
                if not data_analise_final:
                    data_analise_final = date.today().strftime('%d/%m/%Y')

                config['data_analise_inicial'] = data_analise_inicial
                config['data_analise_final'] = data_analise_final

    return config
