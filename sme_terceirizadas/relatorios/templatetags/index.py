from django import template

register = template.Library()


@register.filter
def get_attribute(elemento, atributo):
    return getattr(elemento, atributo, False)


@register.filter
def get_element_by_index(indexable, i):
    return indexable[i]


@register.filter
def index_exists(indexable, i):
    return i <= len(indexable)


@register.filter
def fim_de_fluxo(logs):
    fim = False
    for log in logs:
        if ("neg" in log.status_evento_explicacao or "não" in log.status_evento_explicacao or
            "cancel" in log.status_evento_explicacao):  # noqa
            fim = True
    return fim
