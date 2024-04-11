from django.db.models import Q
from django_filters import rest_framework as filters


class QuestoesPorProdutoFilter(filters.FilterSet):
    ficha_tecnica = filters.CharFilter(
        field_name="ficha_tecnica__uuid",
        lookup_expr="exact",
    )
    questao = filters.CharFilter(method="filtrar_questao")

    def filtrar_questao(self, queryset, name, value):
        return queryset.filter(
            Q(questoes_primarias__questao=value)
            | Q(questoes_secundarias__questao=value)
        ).distinct()
