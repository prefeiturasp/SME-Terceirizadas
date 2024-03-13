from sme_terceirizadas.escola.models import Escola, Lote
from sme_terceirizadas.paineis_consolidados.utils.totalizadores_relatorio_ga import (
    count_query_set_sem_duplicados,
    filtro_geral_totalizadores,
)


def get_dataset_grafico_total_dre_lote(datasets, request, model, instituicao, queryset):
    if isinstance(instituicao, Escola) or request.data.get("unidades_educacionais", []):
        return datasets

    lotes = request.data.get("lotes", [])

    if not lotes:
        lotes = Lote.objects.values_list("uuid", flat=True)
    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros_=None)
    dataset = {"labels": [], "data": []}

    for lote_uuid in lotes:
        lote = Lote.objects.get(uuid=lote_uuid)
        dataset["labels"].append(
            f"{lote.nome} - {lote.diretoria_regional.nome if lote.diretoria_regional else 'sem DRE'}"
        )
        dataset["data"].append(
            count_query_set_sem_duplicados(queryset.filter(lote_uuid=lote_uuid))
        )

    datasets.append(dataset)
    return datasets
