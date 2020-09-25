from django_filters import rest_framework as filters


class DiretoriaRegionalFilter(filters.FilterSet):
    dre = filters.CharFilter(field_name='diretoria_regional__uuid', lookup_expr='iexact')


class AlunoFilter(filters.FilterSet):
    dre = filters.CharFilter(field_name='escola__diretoria_regional__uuid', lookup_expr='iexact')
    escola = filters.CharFilter(field_name='escola__uuid', lookup_expr='iexact')
