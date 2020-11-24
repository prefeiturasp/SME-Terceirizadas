from django_filters import rest_framework as filters


class DiretoriaRegionalFilter(filters.FilterSet):
    dre = filters.CharFilter(field_name='diretoria_regional__uuid', lookup_expr='iexact')


class AlunoFilter(filters.FilterSet):
    codigo_eol = filters.CharFilter(field_name='codigo_eol', lookup_expr='iexact')
    dre = filters.CharFilter(field_name='escola__diretoria_regional__uuid', lookup_expr='iexact')
    escola = filters.CharFilter(field_name='escola__uuid', lookup_expr='iexact')
    nao_tem_dieta_especial = filters.BooleanFilter(field_name='dietas_especiais', lookup_expr='isnull')
