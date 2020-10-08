from django_filters import rest_framework as filters

from ...dados_comuns.fluxo_status import DietaEspecialWorkflow
from ..models import ClassificacaoDieta


class DietaEspecialFilter(filters.FilterSet):
    aluno = filters.CharFilter(field_name='aluno__uuid', lookup_expr='iexact')
    nome_aluno = filters.CharFilter(field_name='aluno__nome', lookup_expr='icontains')
    nome_completo_aluno = filters.CharFilter(field_name='aluno__nome', lookup_expr='icontains')
    cpf_responsavel = filters.CharFilter(field_name='aluno__responsaveis__cpf', lookup_expr='iexact')
    dre = filters.CharFilter(field_name='rastro_dre__uuid', lookup_expr='iexact')
    data_inicial = filters.DateFilter(field_name='criado_em', lookup_expr='date__gte')
    data_final = filters.DateFilter(field_name='criado_em', lookup_expr='date__lte')
    classificacao = filters.ModelMultipleChoiceFilter(field_name='classificacao__id',
                                                      to_field_name='id',
                                                      queryset=ClassificacaoDieta.objects.all())
    status = filters.MultipleChoiceFilter(choices=[(str(state), state) for state in DietaEspecialWorkflow.states])
