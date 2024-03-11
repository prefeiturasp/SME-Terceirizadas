import os
from typing import List

import pandas as pd
from django.http import QueryDict

from sme_terceirizadas.dados_comuns.utils import converte_numero_em_mes
from sme_terceirizadas.escola.models import DiretoriaRegional, Escola, Lote
from sme_terceirizadas.medicao_inicial.models import Medicao, ValorMedicao


def _obtem_medicoes(mes: str, ano: str, filtros: dict):
    return (
        Medicao.objects.select_related("periodo_escolar", "grupo")
        .filter(
            solicitacao_medicao_inicial__mes=mes,
            solicitacao_medicao_inicial__ano=ano,
            solicitacao_medicao_inicial__status="MEDICAO_APROVADA_PELA_CODAE",
            **filtros,
        )
        .exclude(
            solicitacao_medicao_inicial__escola__tipo_unidade__iniciais__in=[
                "CEI",
                "CEI DIRET",
                "CEI INDIR",
                "CEI CEU",
                "CCI",
                "CCI/CIPS",
                "CEU CEI",
                "CEU CEMEI",
                "CEMEI",
            ]
        )
    )


def _obtem_valores_medicao(
    medicao: Medicao,
    tipos_alimentacao: List[str],
):
    queryset = ValorMedicao.objects.select_related("tipo_alimentacao").filter(
        medicao=medicao
    )

    if tipos_alimentacao:
        queryset = queryset.filter(
            tipo_alimentacao__uuid__in=tipos_alimentacao
        ) | queryset.filter(nome_campo="frequencia")

    return queryset.exclude(categoria_medicao__nome__icontains="DIETA")


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
    resultados,
    total_frequencia_por_medicao,
    medicao: Medicao,
    tipos_alimentacao: List[str],
):
    medicao_nome = medicao.nome_periodo_grupo

    if resultados.get(medicao_nome) is None:
        resultados[medicao_nome] = {}
        total_frequencia_por_medicao[medicao_nome] = 0

    valores_medicao = _obtem_valores_medicao(medicao, tipos_alimentacao)
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


def _cria_filtros(query_params: QueryDict):
    filtros = {}

    dre = query_params.get("diretoria_regional")
    if dre:
        filtros["solicitacao_medicao_inicial__escola__diretoria_regional__uuid"] = dre

    lotes = query_params.getlist("lotes[]")
    if lotes:
        filtros["solicitacao_medicao_inicial__escola__lote__uuid__in"] = lotes

    escola = query_params.get("escola")
    if escola:
        escola = escola.split("-")[0].strip()
        filtros["solicitacao_medicao_inicial__escola__codigo_eol"] = escola

    periodos_escolares = query_params.getlist("periodos_escolares[]")
    if periodos_escolares:
        filtros["periodo_escolar__uuid__in"] = periodos_escolares

    return filtros


def obtem_resultados(mes: str, ano: str, query_params: QueryDict):
    tipos_alimentacao = query_params.getlist("tipos_alimentacao[]")

    filtros = _cria_filtros(query_params)
    resultados = {}
    total_frequencia_por_medicao = {}

    medicoes = _obtem_medicoes(mes, ano, filtros)
    for medicao in medicoes:
        resultados = _soma_totais_por_medicao(
            resultados, total_frequencia_por_medicao, medicao, tipos_alimentacao
        )

    return resultados


def _insere_tabela_periodo_na_planilha(aba, refeicoes, colunas, proxima_linha, writer):
    linhas = [[refeicao, *totais.values()] for refeicao, totais in refeicoes.items()]

    df = pd.DataFrame(data=linhas, columns=colunas)

    total_servido = df[colunas[1]].sum()
    total_frequencia = df[colunas[2]].sum()

    totais = pd.DataFrame(
        data=[
            [
                "TOTAL",
                total_servido,
                total_frequencia,
                round(total_servido / total_frequencia, 4),
            ]
        ],
        columns=colunas,
    )

    df = pd.concat([df, totais], ignore_index=True)

    df.to_excel(writer, sheet_name=aba, startrow=proxima_linha, index=False)

    return df


def _formata_filtros(query_params: QueryDict):
    mes, ano = query_params.get("mes_ano").split("_")
    filtros = f"{converte_numero_em_mes(int(mes))} - {ano}"

    dre_uuid = query_params.get("diretoria_regional")
    if dre_uuid:
        dre = DiretoriaRegional.objects.filter(uuid=dre_uuid).first()
        filtros += f" | {dre.nome}"

    lotes_uuid = query_params.getlist("lotes[]")
    if lotes_uuid:
        lotes = Lote.objects.filter(uuid__in=lotes_uuid).values_list("nome", flat=True)
        filtros += f" | {', '.join(lotes)}"

    escola_codigo_eol, *_ = query_params.get("escola").split("-")
    if escola_codigo_eol:
        escola = Escola.objects.filter(codigo_eol=escola_codigo_eol.strip()).first()
        filtros += f" | {escola.nome}"

    return filtros


def _preenche_linha_dos_filtros_selecionados(
    worksheet,
    query_params: QueryDict,
    colunas: List[str],
):
    filtros = _formata_filtros(query_params)

    worksheet.merge_range(1, 0, 1, len(colunas) - 1, filtros.upper())


def _preenche_linha_do_periodo(
    workbook, worksheet, proxima_linha: int, periodo: str, colunas: List[str]
):
    formatacao = workbook.add_format({"bold": True, "font_color": "#006400"})

    worksheet.merge_range(
        proxima_linha - 1,
        0,
        proxima_linha - 1,
        len(colunas) - 1,
        periodo.upper(),
        formatacao,
    )


def _ajusta_layout_header(workbook, worksheet, proxima_linha, df):
    formatacao = workbook.add_format({"bold": True, "bg_color": "#77DD77"})

    worksheet.write_row(
        proxima_linha - len(df.index) - 1, 0, df.columns.values, formatacao
    )


def gera_relatorio_adesao_xlsx(nome_arquivo, resultados, query_params):
    colunas = [
        "Tipo de Alimentação",
        "Total de Alimentações Servidas",
        "Número Total de Frequência",
        "% de Adesão",
    ]

    path = os.path.join(os.path.dirname(__file__), nome_arquivo)

    with pd.ExcelWriter(path) as writer:
        aba = "Relatorio de Adesao"
        proxima_linha = 3  # 3 linhas em branco para o cabecalho
        quantidade_de_linhas_em_branco_apos_tabela = 2

        workbook = writer.book
        worksheet = workbook.add_worksheet(aba)

        _preenche_linha_dos_filtros_selecionados(worksheet, query_params, colunas)

        for periodo, refeicoes in resultados.items():
            df = _insere_tabela_periodo_na_planilha(
                aba, refeicoes, colunas, proxima_linha, writer
            )

            _preenche_linha_do_periodo(
                workbook,
                worksheet,
                proxima_linha,
                periodo,
                colunas,
            )

            proxima_linha += len(df.index) + 1

            _ajusta_layout_header(workbook, worksheet, proxima_linha, df)

            for index, value in enumerate(df.iloc[-1].values):
                formatacao_linha_total = {"bold": True, "bg_color": "#CCCCCC"}

                if index == len(colunas) - 1:
                    formatacao_linha_total["num_format"] = "0.00%"
                else:
                    formatacao_linha_total["num_format"] = "#,##0.00"

                worksheet.write_row(
                    proxima_linha - 1,
                    index,
                    [value],
                    workbook.add_format(formatacao_linha_total),
                )

            proxima_linha += quantidade_de_linhas_em_branco_apos_tabela

        worksheet.set_column(0, len(colunas) - 1, 30)
        worksheet.set_column(
            1, 2, None, workbook.add_format({"num_format": "#,##0.00"})
        )
        worksheet.set_column(
            len(colunas) - 1,
            len(colunas) - 1,
            None,
            workbook.add_format({"num_format": "0.00%"}),
        )
