import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from ..dados_comuns.constants import FLUXO_PARTINDO_DRE
from ..escola.models import Escola
from ..kit_lanche.models import EscolaQuantidade, SolicitacaoKitLancheUnificada
from .utils import formata_logs, get_width


def relatorio_kit_lanche_unificado(request):
    # TODO: colocar permission de requisição
    request_params = request.GET
    uuid_solicitacao = request_params.get('uuid', 'INVALIDO')

    sol = SolicitacaoKitLancheUnificada.objects.get(uuid=uuid_solicitacao)
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
    response['Content-Disposition'] = f'filename="Soliciatao_unificada_{uuid_solicitacao}.pdf"'
    return response
