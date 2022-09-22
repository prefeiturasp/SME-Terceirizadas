from django_filters import rest_framework as filters

from sme_terceirizadas.perfil.models.perfil import Perfil


class VinculoFilter(filters.FilterSet):
    usuario = filters.CharFilter(
        field_name='usuario__username',
        lookup_expr='exact',
    )
    nome = filters.CharFilter(
        field_name='usuario__nome',
        lookup_expr='icontains',
    )
    perfil = filters.CharFilter(
        field_name='perfil__nome',
        lookup_expr='exact',
    )
    visao = filters.MultipleChoiceFilter(
        field_name='perfil__visao',
        choices=Perfil.VISAO_CHOICES,
    )
