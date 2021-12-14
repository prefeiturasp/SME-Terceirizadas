from django_filters import rest_framework as filters

from ..models import Notificacao


class NotificacaoFilter(filters.FilterSet):
    uuid = filters.CharFilter(
        field_name='uuid',
        lookup_expr='exact',
    )
    tipo = filters.MultipleChoiceFilter(
        field_name='tipo',
        choices=[(str(state), state) for state in Notificacao.TIPO_NOTIFICACAO_NOMES],
    )
    categoria = filters.CharFilter(
        field_name='categoria',
        lookup_expr='icontains',
    )
    data_inicial = filters.DateFilter(
        field_name='criado_em__date',
        lookup_expr='gte',
    )
    data_final = filters.DateFilter(
        field_name='criado_em__date',
        lookup_expr='lte',
    )
    lido = filters.BooleanFilter(
        field_name='lido'
    )
