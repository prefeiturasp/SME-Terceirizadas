import os

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import CSS, HTML

from sme_terceirizadas.perfil.models import Usuario

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_pdf(request):
    """Generate pdf."""
    # Model data
    people = Usuario.objects.all()[:50]

    # Rendered
    html_string = render_to_string('cabecalho.html', {'usuarios': people})
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="XXX.pdf"'
    return response
    # return HttpResponse(html_string)
