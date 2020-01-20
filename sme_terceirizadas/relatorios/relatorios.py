import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from . import constants
from .utils import formata_logs, get_width
from ..dieta_especial.models import SolicitacaoDietaEspecial
from ..inclusao_alimentacao.models import GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua
from ..kit_lanche.models import EscolaQuantidade


def relatorio_kit_lanche_unificado(request, solicitacao):
    qtd_escolas = EscolaQuantidade.objects.filter(solicitacao_unificada=solicitacao).count()

    filtro = {'data_de': datetime.date.today(), 'data_para': datetime.date.today() + datetime.timedelta(days=30),
              'tipo_solicitacao': 'TODOS', 'status': 'TODOS'}
    html_string = render_to_string(
        'relatorio2.html',
        {'filtro': filtro, 'solicitacao': solicitacao, 'qtd_escolas': qtd_escolas,
         'fluxo': constants.FLUXO_PARTINDO_DRE, 'width': get_width(constants.FLUXO_PARTINDO_DRE, solicitacao.logs),
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


def relatorio_dieta_especial(request):
    sol = SolicitacaoDietaEspecial.objects.last()
    escola = sol.rastro_escola
    logs = sol.logs
    # Rendered
    html_string = render_to_string(
        'solicitacao_dieta_especial.html',
        {
            'escola': escola,
            'solicitacao': sol,
            'fluxo': constants.FLUXO_DIETA_ESPECIAL,
            'width': get_width(constants.FLUXO_DIETA_ESPECIAL, sol.logs),
            'logs': formata_logs(logs)
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Soliciatao_unificada_{sol.uuid}.pdf"'
    return response


def relatorio_inclusao_alimentacao_continua(request):
    sol = InclusaoAlimentacaoContinua.objects.last()
    escola = sol.rastro_escola
    logs = sol.logs
    # Rendered
    html_string = render_to_string(
        'solicitacao_inclusao_alimentacao_continua.html',
        {
            'escola': escola,
            'solicitacao': sol,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, sol.logs),
            'logs': formata_logs(logs)
        }
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Soliciatao_unificada_{sol.uuid}.pdf"'
    return response


def relatorio_inclusao_alimentacao_normal(request):
    solicitacao = GrupoInclusaoAlimentacaoNormal.objects.last()
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    # Rendered
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
    response['Content-Disposition'] = f'filename="Soliciatao_unificada_{solicitacao.uuid}.pdf"'
    return response
