from django_filters import rest_framework as filters


class DiaParaCorrecaoFilter(filters.FilterSet):
    uuid_solicitacao_medicao = filters.CharFilter(
        field_name="medicao__solicitacao_medicao_inicial__uuid", lookup_expr="iexact"
    )
    nome_grupo = filters.CharFilter(
        field_name="medicao__grupo__nome", lookup_expr="iexact"
    )
    nome_periodo_escolar = filters.CharFilter(
        field_name="medicao__periodo_escolar__nome", lookup_expr="iexact"
    )


class EmpenhoFilter(filters.FilterSet):
    numero = filters.CharFilter(field_name="numero", lookup_expr="icontains")
    contrato = filters.UUIDFilter(method="filtra_contrato")
    edital = filters.UUIDFilter(method="filtra_edital")

    def filtra_contrato(self, queryset, _, value):
        return queryset.filter(contrato__uuid=value)

    def filtra_edital(self, queryset, _, value):
        return queryset.filter(contrato__edital__uuid=value)
