from sme_terceirizadas.medicao_inicial.models import Medicao, ValorMedicao


def obtem_medicoes(mes, ano):
    return Medicao.objects.filter(
        solicitacao_medicao_inicial__mes=mes,
        solicitacao_medicao_inicial__ano=ano,
        solicitacao_medicao_inicial__status="MEDICAO_APROVADA_PELA_CODAE",
    ).exclude(
        solicitacao_medicao_inicial__escola__tipo_unidade__iniciais__in=[
            "CEI",
            "CCI",
            "CEU CEI",
            "CEU CEMEI",
            "CEMEI",
        ]
    )


def obtem_valores_medicao(medicao):
    return ValorMedicao.objects.filter(medicao=medicao).exclude(
        categoria_medicao__nome__icontains="DIETA"
    )


def soma_total_servido_do_tipo_de_alimentacao(resultados, medicao_nome, valor_medicao):
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
