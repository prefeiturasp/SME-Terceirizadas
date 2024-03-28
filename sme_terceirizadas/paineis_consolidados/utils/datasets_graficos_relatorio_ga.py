from sme_terceirizadas.escola.models import (
    DiretoriaRegional,
    Escola,
    Lote,
    TipoUnidadeEscolar,
)
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
            lotes = Lote.objects.filter(
                uuid__in=list(set(queryset.values_list("lote_uuid", flat=True)))
            )
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


def get_dataset_grafico_total_tipo_solicitacao(datasets, request, model, queryset):
    label_data = {
        "AUTORIZADOS": "Autorizadas",
        "CANCELADOS": "Canceladas",
        "NEGADOS": "Negadas",
        "RECEBIDAS": "Recebidas",
    }
    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros_=None)
    dataset = {
        "labels": [],
        "datasets": [
            {
                "label": f"Total de Solicitações {label_data[request.data.get('status')]} por Tipo",
                "data": [],
                "maxBarThickness": 80,
                "backgroundColor": "#d06d12",
            }
        ],
    }

    de_para_tipos_solicitacao = {
        "INC_ALIMENTA": "Inclusão de Alimentação",
        "ALT_CARDAPIO": "Alteração do tipo de Alimentação",
        "KIT_LANCHE_UNIFICADO": "Kit Lanche Unificado",
        "KIT_LANCHE_AVULSA": "Kit Lanche Passeio",
        "INV_CARDAPIO": "Inversão de dia de Cardápio",
        "SUSP_ALIMENTACAO": "Suspensão de Alimentação",
    }

    tipo_doc = request.data.get("tipos_solicitacao", [])

    if not tipo_doc:
        tipo_doc = list(de_para_tipos_solicitacao.keys())

    for tipo_solicitacao in tipo_doc:
        tipos_solicitacao_filtrar = model.map_queryset_por_tipo_doc([tipo_solicitacao])
        dataset["labels"].append(f"{de_para_tipos_solicitacao[tipo_solicitacao]}")
        dataset["datasets"][0]["data"].append(
            count_query_set_sem_duplicados(
                queryset.filter(tipo_doc__in=tipos_solicitacao_filtrar)
            )
        )

    datasets.append(dataset)
    return datasets


def get_dataset_grafico_total_status(datasets, request, model, instituicao):
    label_data = {
        "AUTORIZADOS": "Autorizadas",
        "CANCELADOS": "Canceladas",
        "NEGADOS": "Negadas",
        "RECEBIDAS": "Recebidas",
    }

    cores = {
        "AUTORIZADOS": "#198459",
        "CANCELADOS": "#a50e05",
        "NEGADOS": "#fdc500",
        "RECEBIDAS": "#035d96",
    }

    light_cores = {
        "AUTORIZADOS": "#d4edda",
        "CANCELADOS": "#ff7f7f",
        "NEGADOS": "#fff3cd",
        "RECEBIDAS": "#d1ecf1",
    }

    dataset = {
        "labels": [],
        "datasets": [
            {
                "label": "Total de Solicitações por Status",
                "data": [],
                "maxBarThickness": 80,
                "cutout": "70%",
                "backgroundColor": [],
                "borderColor": [],
            }
        ],
    }

    total = 0

    for status_ in list(label_data.keys()):
        queryset = model.map_queryset_por_status(
            status_, instituicao_uuid=instituicao.uuid
        )
        queryset = filtro_geral_totalizadores(
            request, model, queryset, map_filtros_=None
        )
        total += count_query_set_sem_duplicados(queryset)

    if not total:
        return datasets

    for status_ in list(label_data.keys()):
        queryset = model.map_queryset_por_status(
            status_, instituicao_uuid=instituicao.uuid
        )
        queryset = filtro_geral_totalizadores(
            request, model, queryset, map_filtros_=None
        )

        if queryset.count() == 0:
            continue

        dataset["labels"].append(f"{label_data[status_]}")
        dataset["datasets"][0]["data"].append(
            round(count_query_set_sem_duplicados(queryset) / total * 100, 2)
        )
        dataset["datasets"][0]["backgroundColor"].append(light_cores[status_])
        dataset["datasets"][0]["borderColor"].append(cores[status_])

    datasets.append(dataset)
    return datasets


def get_dataset_grafico_total_tipo_unidade(
    datasets, request, model, instituicao, queryset
):
    if isinstance(instituicao, Escola) or request.data.get("unidades_educacionais", []):
        return datasets

    tipos_unidade = request.data.get("tipos_unidade", [])

    label_data = {
        "AUTORIZADOS": "Autorizadas",
        "CANCELADOS": "Canceladas",
        "NEGADOS": "Negadas",
        "RECEBIDAS": "Recebidas",
    }

    if not tipos_unidade:
        tipos_unidade = TipoUnidadeEscolar.objects.filter(
            pertence_relatorio_solicitacoes_alimentacao=True
        ).values_list("uuid", flat=True)
    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros_=None)
    dataset = {
        "labels": [],
        "datasets": [
            {
                "label": f"Total de Solicitações {label_data[request.data.get('status')]} por Tipo de Unidade",
                "data": [],
                "maxBarThickness": 80,
                "backgroundColor": "#fdc500",
            }
        ],
    }

    for tipo_unidade_uuid in tipos_unidade:
        tipos_unidade = TipoUnidadeEscolar.objects.get(uuid=tipo_unidade_uuid)
        dataset["labels"].append(tipos_unidade.iniciais)
        dataset["datasets"][0]["data"].append(
            count_query_set_sem_duplicados(
                queryset.filter(escola_tipo_unidade_uuid=tipo_unidade_uuid)
            )
        )

    datasets.append(dataset)
    return datasets


def get_dataset_grafico_total_terceirizadas(
    datasets, request, model, instituicao, queryset
):
    if isinstance(instituicao, Escola) or request.data.get("unidades_educacionais", []):
        return datasets

    label_data = {
        "AUTORIZADOS": "Autorizadas",
        "CANCELADOS": "Canceladas",
        "NEGADOS": "Negadas",
        "RECEBIDAS": "Recebidas",
    }

    if isinstance(instituicao, Terceirizada):
        terceirizadas = Terceirizada.objects.filter(id=instituicao.id)
    elif isinstance(instituicao, DiretoriaRegional):
        terceirizadas = Terceirizada.objects.filter(
            uuid__in=list(set(queryset.values_list("terceirizada_uuid", flat=True)))
        )
    else:
        terceirizadas = Terceirizada.objects.filter(
            tipo_empresa=Terceirizada.TERCEIRIZADA
        )

    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros_=None)
    dataset = {
        "labels": [],
        "datasets": [
            {
                "label": f"Total de Solicitações {label_data[request.data.get('status')]} por Empresa Terceirizada",
                "data": [],
                "maxBarThickness": 80,
                "backgroundColor": "#035d96",
            }
        ],
    }

    for terceirizada in terceirizadas:
        dataset["labels"].append(terceirizada.nome_fantasia)
        dataset["datasets"][0]["data"].append(
            count_query_set_sem_duplicados(
                queryset.filter(terceirizada_uuid=terceirizada.uuid)
            )
        )

    datasets.append(dataset)
    return datasets
