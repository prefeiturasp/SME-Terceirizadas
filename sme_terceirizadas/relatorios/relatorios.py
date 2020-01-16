import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from sme_terceirizadas.cardapio.models import AlteracaoCardapio
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario

from ..escola.models import Escola
from ..kit_lanche.models import EscolaQuantidade, SolicitacaoKitLancheUnificada
from .constants import FLUXO_PARTINDO_DRE
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
         'fluxo': FLUXO_PARTINDO_DRE, 'width': get_width(FLUXO_PARTINDO_DRE, sol.logs),
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
    questionamentos = logs.filter(
        status_evento__in=[LogSolicitacoesUsuario.CODAE_QUESTIONOU,
                           LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
                           LogSolicitacoesUsuario.CODAE_AUTORIZOU,
                           LogSolicitacoesUsuario.CODAE_NEGOU]
    ).order_by('criado_em')

    # Rendered
    html_string = render_to_string(
        'solicitacao_alteracao_cardapio.html',
        {'escola': escola, 'solicitacao': sol, 'qtd_escolas': 20, 'substituicoes': substituicoes,
         'questionamentos': questionamentos,
         'fluxo': FLUXO_PARTINDO_DRE, 'width': get_width(FLUXO_PARTINDO_DRE, sol.logs),
         'logs': formata_logs(logs)}
    )
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Soliciatao_unificada_{sol.uuid}.pdf"'
    return response
