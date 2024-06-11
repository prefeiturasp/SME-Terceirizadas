from django_filters import rest_framework as filters


class FormularioSupervisaoFilter(filters.FilterSet):
    uuid = filters.CharFilter(
        field_name="uuid",
        lookup_expr="exact",
    )
    unidade_educacional = filters.CharFilter(
        field_name="escola__uuid",
        lookup_expr="exact",
    )
    data_inicial = filters.DateFilter(
        field_name="formulario_base__data",
        lookup_expr="gte",
    )
    data_final = filters.DateFilter(
        field_name="formulario_base__data",
        lookup_expr="lte",
    )
