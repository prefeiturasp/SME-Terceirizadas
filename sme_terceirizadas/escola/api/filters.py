from django_filters import rest_framework as filters

from sme_terceirizadas.escola.models import Aluno, HistoricoMatriculaAluno


class DiretoriaRegionalFilter(filters.FilterSet):
    dre = filters.CharFilter(
        field_name="diretoria_regional__uuid", lookup_expr="iexact"
    )


class AlunoFilter(filters.FilterSet):
    codigo_eol = filters.CharFilter(field_name="codigo_eol", lookup_expr="iexact")
    dre = filters.CharFilter(
        field_name="escola__diretoria_regional__uuid", lookup_expr="iexact"
    )
    escola = filters.CharFilter(field_name="escola__uuid", method="filter_escola")
    nao_tem_dieta_especial = filters.BooleanFilter(
        field_name="dietas_especiais", lookup_expr="isnull"
    )
    periodo_escolar_nome = filters.CharFilter(
        field_name="periodo_escolar__nome", lookup_expr="iexact"
    )

    def filter_escola(self, queryset, name, value):
        _filter = {name: value}

        alunos_atualmente_na_escola = queryset.filter(**_filter)

        if self.request.query_params.get("inclui_alunos_egressos") != "true":
            return alunos_atualmente_na_escola

        historicos_da_escola = HistoricoMatriculaAluno.objects.filter(**_filter)
        alunos_com_historico_na_escola = Aluno.objects.filter(
            id__in=historicos_da_escola.values_list("aluno_id", flat=True)
        )

        return alunos_atualmente_na_escola | alunos_com_historico_na_escola


class LogAlunosMatriculadosFaixaEtariaDiaFilter(filters.FilterSet):
    escola_uuid = filters.UUIDFilter(field_name="escola__uuid")
    nome_periodo_escolar = filters.CharFilter(field_name="periodo_escolar__nome")
    mes = filters.CharFilter(field_name="data__month", lookup_expr="exact")
    ano = filters.CharFilter(field_name="data__year", lookup_expr="iexact")
