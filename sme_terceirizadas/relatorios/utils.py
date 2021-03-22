import math
from datetime import date
from time import sleep

from django.http import HttpResponse
from django_weasyprint.utils import django_url_fetcher
from weasyprint import HTML

from ..dados_comuns.models import LogSolicitacoesUsuario


def formata_logs(logs):
    if logs.filter(status_evento__in=[
        LogSolicitacoesUsuario.CODAE_AUTORIZOU,
        LogSolicitacoesUsuario.CODAE_NEGOU]
    ).exists():
        logs = logs.exclude(
            status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU)
    return logs.exclude(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO)


def get_width(fluxo, logs):
    logs_formatado = formata_logs(logs)
    fluxo_utilizado = fluxo if len(fluxo) > len(
        logs_formatado) else logs_formatado
    if not fluxo_utilizado:
        return '55%'
    if len(fluxo_utilizado) == 1:
        return '100%'
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


def html_to_pdf_email_anexo(html_string, pdf_filename=None):
    # O PDF gerado aqui pode ser anexado num email.
    # Utilizado para enviar email ao cancelar dietas ativas automaticamente.
    pdf_file = HTML(
        string=html_string,
        url_fetcher=django_url_fetcher,
        base_url='file://abobrinha').write_pdf()
    sleep(5)
    return pdf_file


def get_config_cabecario_relatorio_analise(filtros, data_incial_analise_padrao, contatos_terceirizada):  # noqa C901

    tipos_cabecario = (
        'CABECARIO_POR_DATA',
        'CABECARIO_POR_NOME_TERCEIRIZADA',
        'CABECARIO_REDUZIDO',
        'CABECARIO_POR_NOME')

    config = {
        'cabecario_tipo': None,
        'nome_busca': None,
        'nome_terceirizada': None,
        'email_terceirizada': None,
        'telefone_terceirizada': None,
        'data_analise_inicial': None,
        'data_analise_final': None
    }

    if len(filtros) > 2 or len(filtros) == 0:
        config['cabecario_tipo'] = tipos_cabecario[2]

    if len(filtros) == 1:

        if 'nome_produto' in filtros:
            config['cabecario_tipo'] = tipos_cabecario[3]
            config['nome_busca'] = filtros.get('nome_produto')

        if 'nome_fabricante' in filtros:
            config['cabecario_tipo'] = tipos_cabecario[3]
            config['nome_busca'] = filtros.get('nome_fabricante')

        if 'nome_marca' in filtros:
            config['cabecario_tipo'] = tipos_cabecario[3]
            config['nome_busca'] = filtros.get('nome_marca')

        if 'nome_terceirizada' in filtros:
            config['cabecario_tipo'] = tipos_cabecario[1]
            config['nome_terceirizada'] = filtros.get('nome_terceirizada')
            config['email_terceirizada'] = contatos_terceirizada[0]['email']
            config['telefone_terceirizada'] = contatos_terceirizada[
                0]['telefone']

        if 'data_analise_inicial' in filtros:
            config['cabecario_tipo'] = tipos_cabecario[0]
            config['data_analise_inicial'] = filtros.get(
                'data_analise_inicial')
            config['data_analise_final'] = date.today().strftime('%d/%m/%Y')

        if 'data_analise_final' in filtros:
            config['cabecario_tipo'] = tipos_cabecario[0]
            config['data_analise_inicial'] = data_incial_analise_padrao
            config['data_analise_final'] = filtros.get('data_analise_final')

    elif('data_analise_inicial' in filtros and 'data_analise_final' in filtros):
        config['cabecario_tipo'] = tipos_cabecario[0]
        config['data_analise_inicial'] = filtros.get('data_analise_inicial')
        config['data_analise_final'] = filtros.get('data_analise_final')

    else:
        config['cabecario_tipo'] = tipos_cabecario[2]

    return config


def conta_filtros(filtros):
    qtde_filtros = 0
    filtros.pop('status', [])
    for valor in filtros.values():
        if valor:
            qtde_filtros += 1
    return qtde_filtros


def get_ultima_justificativa_analise_sensorial(produto):
    justificativa = None
    ultimo_log = produto.ultima_homologacao.ultimo_log
    if ultimo_log.status_evento_explicacao == 'CODAE pediu análise sensorial':
        justificativa = ultimo_log.justificativa
    return justificativa
