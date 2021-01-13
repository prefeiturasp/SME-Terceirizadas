from django import template
from sme_terceirizadas.produto.models import Produto


register = template.Library()


@register.filter
def obter_marcas_do_produto(produto):
    marcas = Produto.objects.filter(nome=produto).values_list('marca__nome', flat=True)
    return ', '.join([marca for marca in marcas])
