from django import template

from ...dados_comuns.models import LogSolicitacoesUsuario

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
                                        'CODAE autorizou', 'Terceirizada tomou ciência', 'Escola solicitou inativação',
                                        'CODAE autorizou inativação']:
        return 'active'
    elif log.status_evento_explicacao in ['Escola cancelou', 'DRE cancelou']:
        return 'cancelled'
    elif log.status_evento_explicacao in ['DRE não validou', 'CODAE negou', 'Terceirizada recusou',
                                          'CODAE negou inativação']:
        return 'disapproved'
    elif log.status_evento_explicacao in ['Questionamento pela CODAE']:
        return 'questioned'
    else:
        return 'pending'


@register.filter
def or_logs(fluxo, logs):
    return logs if len(logs) > len(fluxo) else fluxo


@register.filter
def observacao_padrao(observacao, palavra='...'):
    return observacao or f'Sem observações por parte da {palavra}'


@register.filter
def aceita_nao_aceita_str(aceitou):
    if aceitou:
        return 'Aceitou'
    return 'Não aceitou'


@register.filter
def tem_questionamentos(logs):
    return logs.filter(status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU).exists()


@register.filter
def concatena_str(query_set):
    return ', '.join([p.nome for p in query_set])


@register.filter
def concatena_label(query_set):
    label = ''
    for item in query_set:
        label += ' e '.join([tp.nome for tp in item.tipos_alimentacao.all()])
        if item != list(query_set)[-1]:
            label += ', '
    return label
