import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from ..cardapio.models import AlteracaoCardapio
from ..dieta_especial.models import SolicitacaoDietaEspecial
from ..escola.models import Escola
from ..inclusao_alimentacao.models import GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua
from ..kit_lanche.models import EscolaQuantidade, SolicitacaoKitLancheUnificada
from . import constants
from .utils import formata_logs, get_width


def relatorio_kit_lanche_unificado(request):
    sol = SolicitacaoKitLancheUnificada.objects.get(id=1)
    qtd_escolas = EscolaQuantidade.objects.filter(solicitacao_unificada=sol).count()

    """Generate pdf."""
    escola = Escola.objects.first()
    filtro = {'data_de': datetime.date.today(), 'data_para': datetime.date.today() + datetime.timedelta(days=30),
              'tipo_solicitacao': 'TODOS', 'status': 'TODOS'}
    # Rendered
    html_string = render_to_string(
        'relatorio2.html',
        {'escola': escola, 'filtro': filtro, 'solicitacao': sol, 'qtd_escolas': qtd_escolas,
         'fluxo': constants.FLUXO_PARTINDO_DRE, 'width': get_width(constants.FLUXO_PARTINDO_DRE, sol.logs),
         'logs': formata_logs(sol.logs)}
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Soliciatao_unificada_{1}.pdf"'
    return response


def relatorio_alteracao_cardapio(request):
    sol = AlteracaoCardapio.objects.get(uuid='4d2175d9-0aff-4b34-bcf6-9a56eac70521')
    escola = sol.rastro_escola
    substituicoes = sol.substituicoes_periodo_escolar
    logs = sol.logs
    # Rendered
    html_string = render_to_string(
        'solicitacao_alteracao_cardapio.html',
        {'escola': escola, 'solicitacao': sol, 'qtd_escolas': 20, 'substituicoes': substituicoes,
         'fluxo': constants.FLUXO_PARTINDO_ESCOLA, 'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, sol.logs),
         'logs': formata_logs(logs)}
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Soliciatao_unificada_{sol.uuid}.pdf"'
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
