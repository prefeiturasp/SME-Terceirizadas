from django_filters import rest_framework as filters

from ....dados_comuns.fluxo_status import SolicitacaoRemessaWorkFlow
from ...models import Guia


class SolicitacaoFilter(filters.FilterSet):

    numero_requisicao = filters.CharFilter(
        field_name='numero_solicitacao',
        lookup_expr='exact',
        distinct=True
    )
    nome_distribuidor = filters.CharFilter(
        field_name='distribuidor__nome_fantasia__unaccent',
        lookup_expr='icontains',
        distinct=True
    )
    data_inicial = filters.DateFilter(
        field_name='guias__data_entrega',
        lookup_expr='gte',
        distinct=True
    )
    data_final = filters.DateFilter(
        field_name='guias__data_entrega',
        lookup_expr='lte',
        distinct=True
    )
    numero_guia = filters.ModelMultipleChoiceFilter(
        field_name='guias__numero_guia',
        to_field_name='numero_guia',
        queryset=Guia.objects.all(),
        distinct=True
    )
    codigo_unidade = filters.CharFilter(
        field_name='guias__codigo_unidade',
        lookup_expr='exact',
        distinct=True
    )
    nome_unidade = filters.CharFilter(
        field_name='guias__nome_unidade__unaccent',
        lookup_expr='icontains',
        distinct=True
    )
    nome_produto = filters.CharFilter(
        field_name='guias__alimentos__nome_alimento__unaccent',
        lookup_expr='icontains',
        distinct=True
    )
    status = filters.MultipleChoiceFilter(
        field_name='homologacoes__status',
        choices=[(str(state), state) for state in SolicitacaoRemessaWorkFlow.states],
        distinct=True
    )


class GuiaFilter(filters.FilterSet):
    codigo_unidade = filters.CharFilter(
        field_name='codigo_unidade',
        lookup_expr='exact',
        distinct=True
    )
