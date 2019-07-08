"""
Diretoria regional:
- Campos:
    nome, descricao, codigo
"""

import pandas as pd

from sme_pratoaberto_terceirizadas.escola.models import DiretoriaRegional

df = pd.read_excel('/home/amcom/Documents/planilhas/lista_unidades.xlsx', sheet_name='Escolas2801 Consulta')

lista_nomes = [df['DRE'][index] for index in df.index]

lista_elementos = []

for elemento in lista_nomes:
    nome_dre = ""

    for nome in elemento.split()[4:]:
        nome_dre += " " + nome

    if nome_dre not in lista_elementos:
        lista_elementos.append(nome_dre)
        dre = DiretoriaRegional(
            nome=nome_dre
        )
        dre.save()
