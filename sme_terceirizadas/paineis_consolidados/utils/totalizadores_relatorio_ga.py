from sme_terceirizadas.escola.models import Escola, Lote, TipoUnidadeEscolar


def count_query_set_sem_duplicados(query_set):
    return len(set(query_set.values_list("uuid", flat=True)))


def filtro_geral_totalizadores(request, model, queryset, map_filtros_=None):
    tipo_doc = request.data.get("tipos_solicitacao", [])
    tipo_doc = model.map_queryset_por_tipo_doc(tipo_doc)

    unidades_educacionais = request.data.get("unidades_educacionais", [])
    lotes = request.data.get("lotes", [])
    terceirizada = request.data.get("terceirizada", [])
    tipos_unidade = request.data.get("tipos_unidade", [])
    periodo_datas = {
        "data_evento": request.data.get("de", None),
        "data_evento_fim": request.data.get("ate", None),
    }

    queryset = model.busca_periodo_de_datas(
        queryset,
        data_evento=periodo_datas["data_evento"],
        data_evento_fim=periodo_datas["data_evento_fim"],
    )
    if not map_filtros_:
        map_filtros = {
            "lote_uuid__in": lotes,
            "escola_uuid__in": unidades_educacionais,
            "terceirizada_uuid": terceirizada,
            "tipo_doc__in": tipo_doc,
            "escola_tipo_unidade_uuid__in": tipos_unidade,
        }
    else:
        map_filtros = map_filtros_
    filtros = {
        key: value for key, value in map_filtros.items() if value not in [None, []]
    }
    queryset = queryset.filter(**filtros)
    return queryset


def totalizador_rede_municipal(request, queryset, list_cards_totalizadores):
    tipo_doc = request.data.get("tipos_solicitacao", [])
    unidades_educacionais = request.data.get("unidades_educacionais", [])
    lotes = request.data.get("lotes", [])
    terceirizada = request.data.get("terceirizada", [])
    tipos_unidade = request.data.get("tipos_unidade", [])
    periodo_datas = {
        "data_evento": request.data.get("de", None),
        "data_evento_fim": request.data.get("ate", None),
    }

    nenhum_filtro = (
        not tipo_doc
        and not unidades_educacionais
        and not lotes
        and not terceirizada
        and not tipos_unidade
        and not periodo_datas["data_evento"]
        and not periodo_datas["data_evento_fim"]
    )
    if nenhum_filtro:
        key = (
            "Total"
            if request.user.tipo_usuario
            in ["escola", "diretoriaregional", "terceirizada"]
            else "Rede Municipal de Educação"
        )
        list_cards_totalizadores.append({key: count_query_set_sem_duplicados(queryset)})
    return list_cards_totalizadores


def totalizador_total(request, model, queryset, list_cards_totalizadores):
    tipo_doc = request.data.get("tipos_solicitacao", [])
    unidades_educacionais = request.data.get("unidades_educacionais", [])
    lotes = request.data.get("lotes", [])
    terceirizada = request.data.get("terceirizada", [])
    tipos_unidade = request.data.get("tipos_unidade", [])
    periodo_datas = {
        "data_evento": request.data.get("de", None),
        "data_evento_fim": request.data.get("ate", None),
    }

    nenhum_filtro = (
        not tipo_doc
        and not unidades_educacionais
        and not lotes
        and not terceirizada
        and not tipos_unidade
    )

    if (
        nenhum_filtro
        or periodo_datas["data_evento"]
        or periodo_datas["data_evento_fim"]
    ):
        return list_cards_totalizadores

    queryset = filtro_geral_totalizadores(request, model, queryset)
    list_cards_totalizadores.append({"Total": count_query_set_sem_duplicados(queryset)})
    return list_cards_totalizadores


def totalizador_lote(request, model, queryset, list_cards_totalizadores):
    tipo_doc = request.data.get("tipos_solicitacao", [])
    tipo_doc = model.map_queryset_por_tipo_doc(tipo_doc)
    unidades_educacionais = request.data.get("unidades_educacionais", [])
    lotes = request.data.get("lotes", [])
    terceirizada = request.data.get("terceirizada", [])
    tipos_unidade = request.data.get("tipos_unidade", [])

    if not lotes or unidades_educacionais:
        return list_cards_totalizadores

    map_filtros = {
        "tipo_doc__in": tipo_doc,
        "escola_uuid__in": unidades_educacionais,
        "terceirizada_uuid": terceirizada,
        "escola_tipo_unidade_uuid__in": tipos_unidade,
    }
    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros)

    for lote_uuid in lotes:
        lote = Lote.objects.get(uuid=lote_uuid)
        list_cards_totalizadores.append(
            {
                f"{lote.nome} - {lote.diretoria_regional.nome if lote.diretoria_regional else 'sem DRE'}": count_query_set_sem_duplicados(
                    queryset.filter(lote_uuid=lote_uuid)
                )
            }
        )
    return list_cards_totalizadores


def totalizador_tipo_solicitacao(request, model, queryset, list_cards_totalizadores):
    tipo_doc = request.data.get("tipos_solicitacao", [])
    lotes = request.data.get("lotes", [])
    terceirizada = request.data.get("terceirizada", [])
    tipos_unidade = request.data.get("tipos_unidade", [])
    unidades_educacionais = request.data.get("unidades_educacionais", [])

    if not tipo_doc:
        return list_cards_totalizadores

    map_filtros = {
        "lote_uuid__in": lotes,
        "escola_uuid__in": unidades_educacionais,
        "terceirizada_uuid": terceirizada,
        "escola_tipo_unidade_uuid__in": tipos_unidade,
    }
    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros)

    de_para_tipos_solicitacao = {
        "INC_ALIMENTA": "Inclusão de Alimentação",
        "ALT_CARDAPIO": "Alteração do tipo de Alimentação",
        "KIT_LANCHE_UNIFICADO": "Kit Lanche Unificado",
        "KIT_LANCHE_AVULSA": "Kit Lanche Passeio",
        "INV_CARDAPIO": "Inversão de dia de Cardápio",
        "SUSP_ALIMENTACAO": "Suspensão de Alimentação",
    }

    for tipo_solicitacao in tipo_doc:
        tipos_solicitacao_filtrar = model.map_queryset_por_tipo_doc([tipo_solicitacao])
        list_cards_totalizadores.append(
            {
                de_para_tipos_solicitacao[
                    tipo_solicitacao
                ]: count_query_set_sem_duplicados(
                    queryset.filter(tipo_doc__in=tipos_solicitacao_filtrar)
                )
            }
        )
    return list_cards_totalizadores


def totalizador_tipo_unidade(request, model, queryset, list_cards_totalizadores):
    tipo_doc = request.data.get("tipos_solicitacao", [])
    tipo_doc = model.map_queryset_por_tipo_doc(tipo_doc)
    unidades_educacionais = request.data.get("unidades_educacionais", [])
    lotes = request.data.get("lotes", [])
    terceirizada = request.data.get("terceirizada", [])
    tipos_unidade = request.data.get("tipos_unidade", [])

    if not tipos_unidade or unidades_educacionais:
        return list_cards_totalizadores

    map_filtros = {
        "lote_uuid__in": lotes,
        "tipo_doc__in": tipo_doc,
        "terceirizada_uuid": terceirizada,
    }
    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros)

    for tipo_unidade_uuid in tipos_unidade:
        tipo_unidade = TipoUnidadeEscolar.objects.get(uuid=tipo_unidade_uuid)
        list_cards_totalizadores.append(
            {
                tipo_unidade.iniciais: count_query_set_sem_duplicados(
                    queryset.filter(escola_tipo_unidade_uuid=tipo_unidade_uuid)
                )
            }
        )
    return list_cards_totalizadores


def totalizador_unidade_educacional(request, model, queryset, list_cards_totalizadores):
    tipo_doc = request.data.get("tipos_solicitacao", [])
    tipo_doc = model.map_queryset_por_tipo_doc(tipo_doc)
    unidades_educacionais = request.data.get("unidades_educacionais", [])
    terceirizada = request.data.get("terceirizada", [])

    if not unidades_educacionais:
        return list_cards_totalizadores

    map_filtros = {
        "tipo_doc__in": tipo_doc,
        "terceirizada_uuid": terceirizada,
    }
    queryset = filtro_geral_totalizadores(request, model, queryset, map_filtros)

    for unidade_educacional_uuid in unidades_educacionais:
        escola = Escola.objects.get(uuid=unidade_educacional_uuid)
        list_cards_totalizadores.append(
            {
                escola.nome: count_query_set_sem_duplicados(
                    queryset.filter(escola_uuid=unidade_educacional_uuid)
                )
            }
        )
    return list_cards_totalizadores


def totalizador_periodo(request, model, queryset, list_cards_totalizadores):
    queryset = filtro_geral_totalizadores(request, model, queryset)
    periodo_datas = {
        "data_evento": request.data.get("de", None),
        "data_evento_fim": request.data.get("ate", None),
    }

    if periodo_datas["data_evento"] and not periodo_datas["data_evento_fim"]:
        list_cards_totalizadores.append(
            {
                f"Período: a partir de {periodo_datas['data_evento']}": count_query_set_sem_duplicados(
                    queryset
                )
            }
        )
    elif not periodo_datas["data_evento"] and periodo_datas["data_evento_fim"]:
        list_cards_totalizadores.append(
            {
                f"Período: até {periodo_datas['data_evento_fim']}": count_query_set_sem_duplicados(
                    queryset
                )
            }
        )
    elif periodo_datas["data_evento"] and periodo_datas["data_evento_fim"]:
        list_cards_totalizadores.append(
            {
                f"Período: {periodo_datas['data_evento']} até "
                f"{periodo_datas['data_evento_fim']}": count_query_set_sem_duplicados(
                    queryset
                )
            }
        )
    return list_cards_totalizadores
