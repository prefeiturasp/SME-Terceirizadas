"""
Diretoria regional:
- Campos:
    nome, descricao, codigo
"""

import pandas as pd

from sme_pratoaberto_terceirizadas.escola.models import DiretoriaRegional, Lote

df = pd.read_excel('/home/marcelo/Desktop/docs PO alimentacao/lista de lotes.xlsx',
                   sheet_name='Sheet1')

# padroniza os dados
df['DRE'] = df['DRE'].str.strip().str.upper()
df['LOTES'] = df['LOTES'].str.strip().str.upper()
df['LOTE_SIGLA'] = df['LOTE_SIGLA'].str.strip().str.upper()


def cria_dres():
    cont = 0
    for index, row in df.iterrows():
        dre_str = row.DRE
        obj, created = DiretoriaRegional.objects.get_or_create(nome=dre_str)
        if created:
            cont += 1
        print('DRE {} criada? {}'.format(dre_str, created))
    print('quantidade de DRES criadas: {}'.format(cont))


def cria_lotes():
    cont = 0
    for index, row in df.iterrows():
        dre_str = row.DRE
        dre_obj, created_dre = DiretoriaRegional.objects.get_or_create(
            nome=dre_str)

        lote_str = row.LOTES
        sigla_lote_str = row.LOTE_SIGLA
        lote_obj, created_lote = Lote.objects.get_or_create(
            nome=lote_str,
            iniciais=sigla_lote_str,
            diretoria_regional=dre_obj)

        if created_lote:
            cont += 1
        print('Lote {} criado? {}'.format(lote_str, created_lote))
    print('quantidade de LOTES criadas: {}'.format(cont))


cria_dres()
cria_lotes()
