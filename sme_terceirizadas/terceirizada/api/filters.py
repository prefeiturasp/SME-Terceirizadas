from django_filters import rest_framework as filters


class TerceirizadaFilter(filters.FilterSet):

    modulo = filters.CharFilter(
        field_name='emails_terceirizadas__modulo__nome',
        lookup_expr='icontains',
    )


class EmailTerceirizadaPorModuloFilter(filters.FilterSet):

    modulo = filters.CharFilter(
        field_name='modulo__nome',
        lookup_expr='icontains',
    )
