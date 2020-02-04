import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from ..kit_lanche.models import EscolaQuantidade
from . import constants
from .utils import formata_logs, get_width


def relatorio_filtro_periodo(request, query_set_consolidado):
    # TODO: se query_set_consolidado tiver muitos resultados, pode demorar no front-end
    # melhor mandar via celery pro email de quem solicitou
    # ou por padrão manda tudo pro celery
    request_params = request.GET

    tipo_solicitacao = request_params.get('tipo_solicitacao', 'INVALIDO')
    status_solicitacao = request_params.get('status_solicitacao', 'INVALIDO')
    data_inicial = datetime.datetime.strptime(request_params.get('data_inicial'), '%Y-%m-%d')
    data_final = datetime.datetime.strptime(request_params.get('data_final'), '%Y-%m-%d')
    escola_nome = 'ESCOLA'
    dre_nome = 'DRE'
    filtro = {'tipo_solicitacao': tipo_solicitacao, 'status': status_solicitacao,
              'data_inicial': data_inicial, 'data_final': data_final}

    html_string = render_to_string(
        'relatorio_filtro.html',
        {
            'diretoria_regional_nome': dre_nome, 'escola_nome': escola_nome, 'filtro': filtro,
            'query_set_consolidado': query_set_consolidado
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="relatorio_filtro_de_{data_inicial}_ate_{data_final}.pdf"'
    return response


def relatorio_resumo_anual_e_mensal(request):
    resumos_mes = {'total_autorizados': 1821, 'total_negados': 556, 'total_cancelados': 466, 'total_pendentes': 1136,
                   'total_autorizados_mes_passado': 0, 'total_negados_mes_passado': 0,
                   'total_cancelados_mes_passado': 0,
                   'total_pendentes_mes_passado': 0, 'total_mes_atual': 1234, 'total_mes_passado': 333}

    resumo_ano = {'total': 3979,
                  'Inclusão de Alimentação': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                  'Alteração de Cardápio': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                  'Inversão de dia de Cardápio': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                  'Suspensão de Alimentação': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                  'Kit Lanche Passeio': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                  'Kit Lanche Passeio Unificado': {'quantidades': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 0},
                  'Dieta Especial': {'quantidades': [0, 3979, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'total': 3979}}

    meses = range(12)

    escola_nome = 'ESCOLA'
    dre_nome = 'DRE'
    filtro = {'tipo_solicitacao': 'TODOS', 'status': 'TODOS',
              'data_inicial': 'data_inicial', 'data_final': 'data_final'}

    html_string = render_to_string(
        'relatorio_resumo_mes_ano.html',
        {
            'diretoria_regional_nome': dre_nome, 'escola_nome': escola_nome, 'filtro': filtro,
            'resumos_mes': resumos_mes, 'resumo_ano': resumo_ano, 'meses':meses
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="XXXX.pdf"'
    return response


def relatorio_kit_lanche_unificado(request, solicitacao):
    qtd_escolas = EscolaQuantidade.objects.filter(solicitacao_unificada=solicitacao).count()

    html_string = render_to_string(
        'solicitacao_kit_lanche_unificado.html',
        {'solicitacao': solicitacao, 'qtd_escolas': qtd_escolas,
         'fluxo': constants.FLUXO_PARTINDO_DRE,
         'width': get_width(constants.FLUXO_PARTINDO_DRE, solicitacao.logs),
         'logs': formata_logs(solicitacao.logs)}
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="solicitacao_unificada_{solicitacao.id_externo}.pdf"'
    return response


def relatorio_alteracao_cardapio(request, solicitacao):
    escola = solicitacao.rastro_escola
    substituicoes = solicitacao.substituicoes_periodo_escolar
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_alteracao_cardapio.html',
        {'escola': escola,
         'solicitacao': solicitacao,
         'substituicoes': substituicoes,
         'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
         'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
         'logs': formata_logs(logs)}
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="alteracao_cardapio_{solicitacao.id_externo}.pdf"'
    return response


def relatorio_dieta_especial(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_dieta_especial.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'fluxo': constants.FLUXO_DIETA_ESPECIAL,
            'width': get_width(constants.FLUXO_DIETA_ESPECIAL, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="dieta_especial_{solicitacao.id_externo}.pdf"'
    return response


def relatorio_inclusao_alimentacao_continua(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_inclusao_alimentacao_continua.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="inclusao_alimentacao_continua_{solicitacao.id_externo}.pdf"'
    return response


def relatorio_inclusao_alimentacao_normal(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_inclusao_alimentacao_normal.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="inclusao_alimentacao_{solicitacao.id_externo}.pdf"'
    return response


def relatorio_kit_lanche_passeio(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    observacao = solicitacao.solicitacao_kit_lanche.descricao
    solicitacao.observacao = observacao
    html_string = render_to_string(
        'solicitacao_kit_lanche_passeio.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'quantidade_kits': solicitacao.solicitacao_kit_lanche.kits.all().count() * solicitacao.quantidade_alunos,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="solicitacao_avulsa_{solicitacao.id_externo}.pdf"'
    return response


def relatorio_inversao_dia_de_cardapio(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_inversao_de_cardapio.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'data_de': solicitacao.cardapio_de.data,
            'data_para': solicitacao.cardapio_para.data,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="solicitacao_inversao_{solicitacao.id_externo}.pdf"'
    return response


def relatorio_suspensao_de_alimentacao(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    motivo = solicitacao.suspensoes_alimentacao.last().motivo.nome
    suspensoes = solicitacao.suspensoes_alimentacao.all()
    quantidades_por_periodo = solicitacao.quantidades_por_periodo.all()
    html_string = render_to_string(
        'solicitacao_suspensao_de_alimentacao.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'suspensoes': suspensoes,
            'motivo': motivo,
            'quantidades_por_periodo': quantidades_por_periodo,
            'fluxo': constants.FLUXO_INFORMATIVO,
            'width': get_width(constants.FLUXO_INFORMATIVO, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="solicitacao_suspensao_{solicitacao.id_externo}.pdf"'
    return response
