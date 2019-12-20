from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from sme_terceirizadas.perfil.models import Usuario


def generate_pdf(request):
    """Generate pdf."""
    # Model data
    people = Usuario.objects.all()[:50]
    # import pdb
    # pdb.set_trace()

    # Rendered
    html_string = render_to_string('test.html', {'usuarios': people})
    html = HTML(string=html_string)
    result = html.write_pdf()

    return HttpResponse(html_string)
