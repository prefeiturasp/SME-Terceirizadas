from django_filters import rest_framework as filters


class DiaParaCorrecaoFilter(filters.FilterSet):
    uuid_solicitacao_medicao = filters.CharFilter(field_name='medicao__solicitacao_medicao_inicial__uuid',
                                                  lookup_expr='iexact')
    nome_grupo = filters.CharFilter(field_name='medicao__grupo__nome', lookup_expr='iexact')
    nome_periodo_escolar = filters.CharFilter(field_name='medicao__periodo_escolar__nome', lookup_expr='iexact')
