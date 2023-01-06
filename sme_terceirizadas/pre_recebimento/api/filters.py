
from django_filters import rest_framework as filters

from sme_terceirizadas.terceirizada.models import Terceirizada

from ...dados_comuns.fluxo_status import CronogramaWorkflow


class CronogramaFilter(filters.FilterSet):

    uuid = filters.CharFilter(
        field_name='uuid',
        lookup_expr='exact',
    )
    numero = filters.CharFilter(
        field_name='numero',
        lookup_expr='icontains',
    )
    nome_empresa = filters.CharFilter(
        field_name='nome_empresa',
        lookup_expr='icontains',
    )
    nome_produto = filters.CharFilter(
        field_name='nome_produto',
        lookup_expr='icontains',
    )
    data_inicial = filters.DateFilter(
        field_name='etapas__data_programada',
        lookup_expr='gte',
    )
    data_final = filters.DateFilter(
        field_name='etapas__data_programada',
        lookup_expr='lte',
    )
    status = filters.MultipleChoiceFilter(
        field_name='status',
        choices=[(str(state), state) for state in CronogramaWorkflow.states],
    )
    armazem = filters.ModelMultipleChoiceFilter(
        field_name='armazem__uuid',
        to_field_name='uuid',
        queryset=Terceirizada.objects.filter(tipo_empresa=Terceirizada.ARMAZEM_DISTRIBUIDOR),
    )
