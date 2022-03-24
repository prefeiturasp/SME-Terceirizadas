from django_filters import rest_framework as filters

from ..models import CentralDeDownload, Notificacao


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


class CentralDeDownloadFilter(filters.FilterSet):
    uuid = filters.CharFilter(
        field_name='uuid',
        lookup_expr='exact',
    )
    identificador = filters.CharFilter(
        field_name='identificador',
        lookup_expr='exact',
    )
    status = filters.MultipleChoiceFilter(
        field_name='status',
        choices=[(str(status), status) for status in CentralDeDownload.STATUS_NOMES],
    )
    data_geracao = filters.DateFilter(
        field_name='criado_em__date',
        lookup_expr='exact',
    )
    visto = filters.BooleanFilter(
        field_name='visto'
    )
