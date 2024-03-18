from sme_terceirizadas.escola.models import DiretoriaRegional, Escola, Lote
from sme_terceirizadas.paineis_consolidados.utils.totalizadores_relatorio_ga import (
    count_query_set_sem_duplicados,
    filtro_geral_totalizadores,
)
from sme_terceirizadas.terceirizada.models import Terceirizada


def get_dataset_grafico_total_dre_lote(datasets, request, model, instituicao, queryset):
    if isinstance(instituicao, Escola) or request.data.get("unidades_educacionais", []):
        return datasets

    lotes = request.data.get("lotes", [])

    label_data = {
        "AUTORIZADOS": "Autorizadas",
        "CANCELADOS": "Canceladas",
        "NEGADOS": "Negadas",
        "RECEBIDAS": "Recebidas",
    }

    if not lotes:
        if isinstance(instituicao, Terceirizada):
            lotes = Lote.objects.filter(terceirizada=instituicao)
        elif isinstance(instituicao, DiretoriaRegional):
            lotes = Lote.objects.filter(diretoria_regional=instituicao)
        else:
            lotes = Lote.objects.all()
        lotes = lotes.values_list("uuid", flat=True)
    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros_=None)
    dataset = {
        "labels": [],
        "datasets": [
            {
                "label": f"Total de Solicitações {label_data[request.data.get('status')]} por DRE e Lote",
                "data": [],
                "maxBarThickness": 80,
                "backgroundColor": "#198459",
            }
        ],
    }

    for lote_uuid in lotes:
        lote = Lote.objects.get(uuid=lote_uuid)
        dataset["labels"].append(
            f"{lote.nome} - {lote.diretoria_regional.nome if lote.diretoria_regional else 'sem DRE'}"
        )
        dataset["datasets"][0]["data"].append(
            count_query_set_sem_duplicados(queryset.filter(lote_uuid=lote_uuid))
        )

    datasets.append(dataset)
    return datasets
