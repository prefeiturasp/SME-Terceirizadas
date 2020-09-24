from django_filters import rest_framework as filters

from ...dados_comuns.fluxo_status import DietaEspecialWorkflow
from ..models import AlergiaIntolerancia, ClassificacaoDieta


class DietaEspecialFilter(filters.FilterSet):
    nome_aluno = filters.CharFilter(field_name='aluno__nome', lookup_expr='icontains')
    dre = filters.CharFilter(field_name='rastro_dre__uuid', lookup_expr='iexact')
    diagnostico = filters.ModelMultipleChoiceFilter(field_name='alergias_intolerancias__id',
                                                    to_field_name='id',
                                                    queryset=AlergiaIntolerancia.objects.all())
    data_inicial = filters.DateFilter(field_name='criado_em', lookup_expr='date__gte')
    data_final = filters.DateFilter(field_name='criado_em', lookup_expr='date__lte')
    classificacao = filters.ModelMultipleChoiceFilter(field_name='classificacao__id',
                                                      to_field_name='id',
                                                      queryset=ClassificacaoDieta.objects.all())
    status = filters.MultipleChoiceFilter(choices=[(str(state), state) for state in DietaEspecialWorkflow.states])
