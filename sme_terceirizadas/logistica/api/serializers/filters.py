from django_filters import rest_framework as filters

from ....dados_comuns.fluxo_status import SolicitacaoRemessaWorkFlow


class SolicitacaoFilter(filters.FilterSet):

    numero_requisicao = filters.CharFilter(
        field_name='numero_solicitacao',
        lookup_expr='exact',
    )
    nome_distribuidor = filters.CharFilter(
        field_name='distribuidor__nome_fantasia',
        lookup_expr='icontains',
    )
    data_inicial = filters.DateFilter(
        field_name='guias__data_entrega',
        lookup_expr='gte',
    )
    data_final = filters.DateFilter(
        field_name='guias__data_entrega',
        lookup_expr='lte',
    )
    numero_guia = filters.CharFilter(
        field_name='guias__numero_guia',
        lookup_expr='exact',
    )
    codigo_unidade = filters.CharFilter(
        field_name='guias__codigo_unidade',
        lookup_expr='exact',
    )
    nome_unidade = filters.CharFilter(
        field_name='guias__nome_unidade__unaccent',
        lookup_expr='icontains',
    )
    nome_produto = filters.CharFilter(
        field_name='guias__alimentos__nome_alimento',
        lookup_expr='icontains',
    )
    status = filters.MultipleChoiceFilter(
        field_name='status',
        choices=[(str(state), state) for state in SolicitacaoRemessaWorkFlow.states],
    )


class GuiaFilter(filters.FilterSet):
    codigo_unidade = filters.CharFilter(
        field_name='codigo_unidade',
        lookup_expr='exact',

    )
