"""
Diretoria regional:
- Campos:
    nome, descricao, codigo
"""

from unicodedata import normalize

import pandas as pd

from sme_pratoaberto_terceirizadas.escola.models import TipoUnidadeEscolar

df = pd.read_excel('/home/marcelo/Desktop/docs PO alimentacao/escola_dre_codae.xlsx',
                   converters={'EOL': str,
                               'TELEFONE2': str,
                               'COD. CODAE': str
                               },
                   sheet_name='EMEF_EMEFM_EMEBS_CIEJA')


def normaliza_nome(nome):
    nome = nome.replace(' / ', '/')
    nome = normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return nome


def coloca_zero_a_esquerda(palavra, tam=6):
    tam_palavra = len(palavra)
    qtd_zeros = tam - tam_palavra
    zeros = '0' * qtd_zeros
    final = ''
    if tam_palavra < tam:
        final = zeros + palavra
    return final or palavra


# padroniza os dados
df['EOL'] = df['EOL'].str.strip().str.upper()
df['EOL'] = df['EOL'].apply(coloca_zero_a_esquerda)

df['TIPO DE U.E'] = df['TIPO DE U.E'].str.strip().str.upper()
df['TIPO DE U.E'] = df['TIPO DE U.E'].apply(normaliza_nome)

df['NOME'] = df['NOME'].str.strip().str.upper()

df['DRE'] = df['DRE'].str.strip().str.upper()
df['DRE'] = df['DRE'].apply(normaliza_nome)

df['SIGLA/LOTE'] = df['SIGLA/LOTE'].str.strip().str.upper()
df['E-MAIL'] = df['E-MAIL'].str.strip().str.upper()
df['ENDEREÇO'] = df['ENDEREÇO'].str.strip().str.upper()
df['Nº'] = df['Nº'].str.strip().str.upper()
df['BAIRRO'] = df['BAIRRO'].str.strip().str.upper()
df['CEP'] = df['CEP'].str.strip().str.upper()
df['TELEFONE'] = df['TELEFONE'].str.strip().str.upper()
df['TELEFONE2'] = df['TELEFONE2'].str.strip().str.upper()
df['EMPRESA'] = df['EMPRESA'].str.strip().str.upper()
df['COD. CODAE'] = df['COD. CODAE'].str.strip().str.upper()
df['TIPO_UE2'] = df['TIPO_UE2'].str.strip().str.upper()


def cria_unidade_escolar():
    cont = 0
    for index, row in df.iterrows():
        iniciais = row['TIPO DE U.E']
        obj, created = TipoUnidadeEscolar.objects.get_or_create(iniciais=iniciais)
        if created:
            cont += 1
            print('UNIDADE ESCOLAR {} CRIADO'.format(obj))
    print('qtd ue criados... {}'.format(cont))


cria_unidade_escolar()
