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
        if ('neg' in log.status_evento_explicacao or 'não' in log.status_evento_explicacao or
            'cancel' in log.status_evento_explicacao):  # noqa
            fim = True
    return fim


@register.filter  # noqa
def class_css(log):
    if log.status_evento_explicacao in ['Solicitação Realizada', 'Escola revisou', 'DRE validou', 'DRE revisou',
                                        'CODAE autorizou', 'Terceirizada tomou ciência']:
        return 'active'
    elif log.status_evento_explicacao in ['Escola cancelou', 'DRE cancelou']:
        return 'cancelled'
    elif log.status_evento_explicacao in ['DRE não validou', 'CODAE negou', 'Terceirizada recusou']:
        return 'disapproved'
    elif log.status_evento_explicacao in ['Questionamento pela CODAE']:
        return 'questioned'
    else:
        return 'pending'


@register.filter
def or_logs(fluxo, logs):
    return logs if len(logs) > len(fluxo) else fluxo
