import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from ..escola.models import Escola
from ..kit_lanche.models import SolicitacaoKitLancheUnificada, EscolaQuantidade


def generate_pdf(request):
    sol = SolicitacaoKitLancheUnificada.objects.first()
    qtd_escolas = EscolaQuantidade.objects.filter(solicitacao_unificada=sol).count()

    """Generate pdf."""
    escola = Escola.objects.first()
    filtro = {'data_de': datetime.date.today(), 'data_para': datetime.date.today() + datetime.timedelta(days=30),
              'tipo_solicitacao': 'TODOS', 'status': 'TODOS'}
    # Rendered
    html_string = render_to_string('relatorio2.html',
                                   {'escola': escola, 'filtro': filtro, "solicitacao": sol, 'qtd_escolas': qtd_escolas
                                    })
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="XXX.pdf"'
    return response
