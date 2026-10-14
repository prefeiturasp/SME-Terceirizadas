"""
Excel do Relatório de Alimentações Servidas.
"""

import io
import re
from datetime import datetime

import pandas as pd

from src.dados_comuns.constants import FORMATO_DATA_BRASILEIRO
from src.medicao_inicial.services.relatorio_alimentacoes_servidas_dados import (
    SECAO_DIETA_TIPO_A,
    SECAO_DIETA_TIPO_B,
    SECAO_REGULAR,
    SECOES,
    soma_colunas,
)
from src.medicao_inicial.services.relatorio_alimentacoes_servidas_dados import (
    total_geral as calcula_total_geral,
)

NOME_ABA = "Alimentações Servidas"
LIMITE_NOME_ABA = 31
LOGO = "src/relatorios/static/images/logo-sigpae.png"
CONSOLIDACAO_TOTAL_GERAL = "Consolidação - Total Geral"
ROTULO_TIPO_ALIMENTACAO = "Tipo de Alimentação"
ROTULO_CATEGORIA = "Categoria"
ROTULO_TOTAL_GERAL = "TOTAL GERAL"

ALTURA_TITULO = 70
# A logo (598x506 px a 72 dpi) escalada em 0.08 ocupa cerca de 54 px de altura;
# a linha do título tem ALTURA_TITULO pontos (1 pt = 4/3 px).
ALTURA_LOGO_PX = 54
LOGO_DESLOCAMENTO_X = 50
LOGO_DESLOCAMENTO_Y = round((ALTURA_TITULO * 4 / 3 - ALTURA_LOGO_PX) / 2)

# Verdes do relatório de ateste financeiro, do mais claro ao mais escuro.
COR_CABECALHO = "#0B8A5A"
COR_SECAO = {
    SECAO_REGULAR: "#E6F4EA",
    SECAO_DIETA_TIPO_A: "#B1DBB7",
    SECAO_DIETA_TIPO_B: "#67A37E",
}
COR_GRUPO = "#D9D9D9"
COR_TOTAL = "#EFECEC"


class _Planilha:
    def __init__(self, workbook, relatorio, nome_aba, formatos, indices):
        self.workbook = workbook
        self.worksheet = workbook.add_worksheet(nome_aba)
        self.indices = indices
        self.colunas = [
            *(relatorio["colunas"][indice] for indice in indices),
            relatorio["coluna_total"],
        ]
        self.ultima_coluna = len(self.colunas)
        self.tamanho = len(relatorio["colunas"])
        self.linha = 0
        self.formatos = formatos

    def faixa_mesclada(self, texto, formato, altura):
        self.worksheet.merge_range(
            self.linha, 0, self.linha, self.ultima_coluna, texto, self.formatos[formato]
        )
        self.worksheet.set_row(self.linha, altura)
        self.linha += 1

    def cabecalho(self, rotulo):
        self.worksheet.write_row(
            self.linha, 0, [rotulo, *self.colunas], self.formatos["cabecalho"]
        )
        self.worksheet.set_row(self.linha, 45)
        self.linha += 1

    def linha_valores(self, rotulo, valores, formato):
        valores = [valores[indice] for indice in self.indices]
        self.worksheet.write(self.linha, 0, rotulo, self.formatos[f"{formato}_texto"])
        self.worksheet.write_row(
            self.linha, 1, [*valores, sum(valores)], self.formatos[formato]
        )
        self.worksheet.set_row(self.linha, 30)
        self.linha += 1

    def pula(self, linhas=1):
        self.linha += linhas


def _formatos(workbook):
    base = {"align": "center", "valign": "vcenter", "border": 1}
    formatos = {
        "titulo": workbook.add_format(
            {
                "bold": True,
                "bg_color": "#C1F2B0",
                "align": "center",
                "valign": "vcenter",
            }
        ),
        "informacao": workbook.add_format({"valign": "vcenter", "text_wrap": True}),
        "filtros": workbook.add_format(
            {"bold": True, "valign": "vcenter", "text_wrap": True}
        ),
        "grupo": workbook.add_format(
            {
                "bold": True,
                "font_color": "#000000",
                "bg_color": COR_GRUPO,
                "align": "center",
                "valign": "vcenter",
            }
        ),
        "cabecalho": workbook.add_format(
            {
                **base,
                "bold": True,
                "font_color": "#FFFFFF",
                "bg_color": COR_CABECALHO,
                "text_wrap": True,
            }
        ),
        "normal": workbook.add_format({**base, "num_format": "#,##0"}),
        "normal_texto": workbook.add_format({**base, "align": "left"}),
        "total": workbook.add_format(
            {**base, "bold": True, "bg_color": COR_TOTAL, "num_format": "#,##0"}
        ),
        "total_texto": workbook.add_format(
            {**base, "bold": True, "bg_color": COR_TOTAL, "align": "left"}
        ),
    }
    for secao, cor in COR_SECAO.items():
        formatos[secao] = workbook.add_format(
            {**base, "bold": True, "bg_color": cor, "align": "left"}
        )
    return formatos


def gera_relatorio_alimentacoes_servidas_xlsx(relatorio):
    arquivo = io.BytesIO()
    with pd.ExcelWriter(arquivo, engine="xlsxwriter") as writer:
        abas = _Abas(writer.book, relatorio)
        grupos = relatorio["grupos"]
        if len(grupos) > 1:
            for grupo in grupos:
                planilha = abas.nova(_unidades_do_grupo(grupo), grupo["colunas"])
                _escreve_grupo(planilha, grupo)
                _escreve_consolidacao(planilha, _total_geral_do_grupo(grupo, relatorio))
        else:
            planilha = abas.nova(NOME_ABA, _colunas_com_registro(relatorio))
            for grupo in grupos:
                _escreve_grupo(planilha, grupo)
            _escreve_consolidacao(planilha, relatorio["total_geral"])
    return arquivo.getvalue()


class _Abas:
    """Cria as abas com cabeçalho e larguras, compartilhando os formatos."""

    def __init__(self, workbook, relatorio):
        self.workbook = workbook
        self.relatorio = relatorio
        self.formatos = _formatos(workbook)
        self.nomes = set()

    def nova(self, nome, indices):
        planilha = _Planilha(
            self.workbook,
            self.relatorio,
            self._nome_unico(nome),
            self.formatos,
            indices,
        )
        _ajusta_colunas(planilha)
        _escreve_cabecalho(planilha, self.relatorio)
        return planilha

    def _nome_unico(self, nome):
        """Nome de aba único (o Excel ignora maiúsculas e minúsculas)."""
        base = _nome_aba(nome)
        candidato, repeticao = base, 1
        while candidato.upper() in self.nomes:
            repeticao += 1
            sufixo = f" ({repeticao})"
            candidato = f"{base[: LIMITE_NOME_ABA - len(sufixo)]}{sufixo}"
        self.nomes.add(candidato.upper())
        return candidato


def _colunas_com_registro(relatorio):
    """Colunas com lançamento em algum grupo; sem dados, todas as colunas."""
    com_registro = {
        indice for grupo in relatorio["grupos"] for indice in grupo["colunas"]
    }
    return sorted(com_registro) or list(range(len(relatorio["colunas"])))


def _nome_aba(nome):
    """Nome válido de aba do Excel: sem ``[]:*?/\\`` e com até 31 caracteres."""
    return re.sub(r"[\[\]:*?/\\]", " ", nome)[:LIMITE_NOME_ABA].strip() or NOME_ABA


def _unidades_do_grupo(grupo):
    return ", ".join(grupo["tipos_unidades"]).upper()


def _total_geral_do_grupo(grupo, relatorio):
    """Total geral apenas das unidades do grupo, a partir do próprio detalhe."""
    return calcula_total_geral([grupo], len(relatorio["colunas"]))


def _ajusta_colunas(planilha):
    planilha.worksheet.set_column(0, 0, 40)
    planilha.worksheet.set_column(1, planilha.ultima_coluna, 16)


def _escreve_cabecalho(planilha, relatorio):
    planilha.faixa_mesclada(relatorio["titulo"], "titulo", ALTURA_TITULO)
    planilha.worksheet.insert_image(
        0,
        0,
        LOGO,
        {
            "x_offset": LOGO_DESLOCAMENTO_X,
            "y_offset": LOGO_DESLOCAMENTO_Y,
            "x_scale": 0.08,
            "y_scale": 0.08,
        },
    )
    planilha.faixa_mesclada(_texto_filtros(relatorio), "filtros", 40)
    data = datetime.now().date().strftime(FORMATO_DATA_BRASILEIRO)
    planilha.faixa_mesclada(f"Data: {data}", "informacao", 30)
    planilha.pula()


def _texto_filtros(relatorio):
    # Meses e recreios já aparecem nas colunas.
    partes = [", ".join(relatorio["dres"])]
    if relatorio["periodo_lancamento_de"]:
        partes.append(
            f"Período de lançamento: de {relatorio['periodo_lancamento_de']} "
            f"até {relatorio['periodo_lancamento_ate']}"
        )
    return " | ".join(partes).upper()


def _escreve_grupo(planilha, grupo):
    planilha.faixa_mesclada(_unidades_do_grupo(grupo), "grupo", 35)
    planilha.cabecalho(ROTULO_TIPO_ALIMENTACAO)
    for secao in SECOES:
        planilha.faixa_mesclada(secao, secao, 30)
        for nome, valores in grupo["alimentacoes"][secao].items():
            planilha.linha_valores(nome, valores, "normal")
    planilha.pula()


def _escreve_consolidacao(planilha, total_geral):
    planilha.faixa_mesclada(CONSOLIDACAO_TOTAL_GERAL.upper(), "grupo", 35)
    _escreve_total_geral(planilha, total_geral)


def _escreve_total_geral(planilha, total_geral):
    planilha.cabecalho(ROTULO_CATEGORIA)
    for secao in SECOES:
        planilha.linha_valores(secao, total_geral[secao], "normal")
    total = soma_colunas(total_geral.values(), planilha.tamanho)
    planilha.linha_valores(ROTULO_TOTAL_GERAL, total, "total")
