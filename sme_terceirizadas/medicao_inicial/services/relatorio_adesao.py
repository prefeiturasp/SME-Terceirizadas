from sme_terceirizadas.medicao_inicial.models import Medicao, ValorMedicao


def _obtem_medicoes(mes: str, ano: str):
    return (
        Medicao.objects.select_related("periodo_escolar", "grupo")
        .filter(
            solicitacao_medicao_inicial__mes=mes,
            solicitacao_medicao_inicial__ano=ano,
            solicitacao_medicao_inicial__status="MEDICAO_APROVADA_PELA_CODAE",
        )
        .exclude(
            solicitacao_medicao_inicial__escola__tipo_unidade__iniciais__in=[
                "CEI",
                "CCI",
                "CEU CEI",
                "CEU CEMEI",
                "CEMEI",
            ]
        )
    )


def _obtem_valores_medicao(medicao: Medicao):
    return (
        ValorMedicao.objects.select_related("tipo_alimentacao")
        .filter(medicao=medicao)
        .exclude(categoria_medicao__nome__icontains="DIETA")
    )


def _soma_total_servido_do_tipo_de_alimentacao(
    resultados, medicao_nome: str, valor_medicao: ValorMedicao
):
    tipo_alimentacao = valor_medicao.tipo_alimentacao

    if tipo_alimentacao is not None:
        if resultados[medicao_nome].get(tipo_alimentacao.nome) is None:
            resultados[medicao_nome][tipo_alimentacao.nome] = {
                "total_servido": 0,
                "total_frequencia": 0,
                "total_adesao": 0,
            }

        resultados[medicao_nome][tipo_alimentacao.nome]["total_servido"] += int(
            valor_medicao.valor
        )

    return resultados


def _atualiza_total_frequencia_e_adesao_para_cada_tipo_de_alimentacao(
    resultados, medicao_nome: str, total_frequencia: int
):
    for tipo_alimentacao in resultados[medicao_nome].keys():
        tipo_alimentacao_totais = resultados[medicao_nome][tipo_alimentacao]
        tipo_alimentacao_totais["total_frequencia"] = total_frequencia
        tipo_alimentacao_totais["total_adesao"] = round(
            tipo_alimentacao_totais["total_servido"] / total_frequencia,
            4,
        )

    return resultados


def _soma_totais_por_medicao(
    resultados, total_frequencia_por_medicao, medicao: Medicao
):
    medicao_nome = (
        medicao.periodo_escolar.nome if medicao.periodo_escolar else medicao.grupo.nome
    )

    if resultados.get(medicao_nome) is None:
        resultados[medicao_nome] = {}
        total_frequencia_por_medicao[medicao_nome] = 0

    valores_medicao = _obtem_valores_medicao(medicao)
    for valor_medicao in valores_medicao:
        if valor_medicao.nome_campo == "frequencia":
            total_frequencia_por_medicao[medicao_nome] += int(valor_medicao.valor)
        else:
            resultados = _soma_total_servido_do_tipo_de_alimentacao(
                resultados, medicao_nome, valor_medicao
            )

    if not resultados[medicao_nome]:
        del resultados[medicao_nome]
    else:
        resultados = _atualiza_total_frequencia_e_adesao_para_cada_tipo_de_alimentacao(
            resultados, medicao_nome, total_frequencia_por_medicao[medicao_nome]
        )

    return resultados


def obtem_resultados(mes: str, ano: str):
    resultados = {}
    total_frequencia_por_medicao = {}

    medicoes = _obtem_medicoes(mes, ano)
    for medicao in medicoes:
        resultados = _soma_totais_por_medicao(
            resultados, total_frequencia_por_medicao, medicao
        )

    return resultados
