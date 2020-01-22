from django import template
register = template.Library()


@register.filter
def translate_movimentacao(movimentacao_realizada):
    if movimentacao_realizada == 'DRE_VALIDADO':
        return 'foi validada'
    elif movimentacao_realizada == 'DRE_NAO_VALIDOU_PEDIDO_ESCOLA':
        return 'não foi validada'
    elif movimentacao_realizada == 'ESCOLA_CANCELOU':
        return 'foi cancelada pela escola'
    elif movimentacao_realizada == 'DRE_CANCELOU':
        return 'foi cancelada pela DRE'
    elif movimentacao_realizada == 'CODAE_AUTORIZADO':
        return 'foi autorizada'
    elif movimentacao_realizada == 'CODAE_NEGOU_PEDIDO':
        return 'não foi autorizada'
    else:
        return ''


