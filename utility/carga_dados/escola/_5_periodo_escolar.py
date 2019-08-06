import numpy as np
import pandas as pd

from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar, Escola
from utility.carga_dados.escola.helper import coloca_zero_a_esquerda

df = pd.read_excel('/home/amcom/Documentos/docs PO alimentacao/CADASTRO ESCOLAS DIVULGACAO.xlsx',
                   converters={
                       'ANO': str,
                       'CODESC': str,
                       'NUMERO': str,
                       'CEP': str,
                       'TEL1': str,
                       'TEL2': str,
                       'FAX': str,
                       'CDIST': str,
                       'SETOR': str,
                       'CODSEE': str,
                       'CODINEP': str,
                       'EH': str,
                       'TOTCLA': str,
                       'TOTALU': int,
                       'TOTALU_COM_COMPAT': str,
                       'DATABASE': str,
                       'DTURNOS': str
                   },
                   sheet_name='CADASTRO_ESCOLAS_DIVULGACAO')

df = df.replace(np.nan, '', regex=True)
df['ANO'] = df['ANO'].str.strip().str.upper()

df['CODESC'] = df['CODESC'].str.strip().str.upper()
df['CODESC'] = df['CODESC'].apply(coloca_zero_a_esquerda)

df['TIPOESC'] = df['TIPOESC'].str.strip().str.upper()
df['NOMESC'] = df['NOMESC'].str.strip().str.upper()
df['DRE'] = df['DRE'].str.strip().str.upper()
df['DIRETORIA'] = df['DIRETORIA'].str.strip().str.upper()
df['SUBPREF'] = df['SUBPREF'].str.strip().str.upper()
df['CEU'] = df['CEU'].str.strip().str.upper()
df['ENDERECO'] = df['ENDERECO'].str.strip().str.upper()
df['NUMERO'] = df['NUMERO'].str.strip().str.upper()
df['BAIRRO'] = df['BAIRRO'].str.strip().str.upper()
df['CEP'] = df['CEP'].str.strip().str.upper()
df['TEL1'] = df['TEL1'].str.strip().str.upper()
df['TEL2'] = df['TEL2'].str.strip().str.upper()
df['FAX'] = df['FAX'].str.strip().str.upper()
df['SITUACAO'] = df['SITUACAO'].str.strip().str.upper()
df['CDIST'] = df['CDIST'].str.strip().str.upper()
df['DISTRITO'] = df['DISTRITO'].str.strip().str.upper()
df['SETOR'] = df['SETOR'].str.strip().str.upper()
df['CODSEE'] = df['CODSEE'].str.strip().str.upper()
df['CODINEP'] = df['CODINEP'].str.strip().str.upper()
df['EH'] = df['EH'].str.strip().str.upper()
df['NOME_ANT'] = df['NOME_ANT'].str.strip().str.upper()
df['T2D3D'] = df['T2D3D'].str.strip().str.upper()

df['DTURNOS'] = df['DTURNOS'].str.strip().str.upper()

df['REDE'] = df['REDE'].str.strip().str.upper()
df['DATABASE'] = df['DATABASE'].str.strip().str.upper()
df['TOTCLA'] = df['TOTCLA'].str.strip().str.upper()
df['TOTALU'] = df['TOTALU']
df['TOTALU_COM_COMPAT'] = df['TOTALU_COM_COMPAT'].str.strip().str.upper()

depara = {'G': 'INTEGRAL',
          'M': 'MANHA',
          'T': 'TARDE',
          'N': 'NOITE',
          'I': 'INTEGRAL',
          'V': 'TARDE'
          }


def cria_periodo_escolar():
    cont = 0
    for periodo in depara.values():
        obj, created = PeriodoEscolar.objects.get_or_create(nome=periodo)
        if created:
            cont += 1
            print(f'PERIODO ESCOLAR {obj} CRIADO')
    print(f'qtd  criados... {cont}')


def vincula_periodo_escolar_a_escola():
    cont = 0
    for index, row in df.iterrows():
        periodos_str = row.DTURNOS
        cod_eol = row.CODESC
        total_alunos = row.TOTALU
        try:
            escola = Escola.objects.get(codigo_eol=cod_eol) or None
            if total_alunos:
                escola.quantidade_alunos = total_alunos
        except:
            continue

        periodo_escolar_lista = []
        for periodo_letra in periodos_str:
            print(f'{escola} -> {periodo_letra}')
            periodo_obj = PeriodoEscolar.objects.get(nome=depara.get(periodo_letra))
            periodo_escolar_lista.append(periodo_obj)
        escola.periodos_escolares.set(periodo_escolar_lista)
        escola.save()
        cont += 1
        print(f'escola {escola} tem {len(periodo_escolar_lista)} periodos escolares')

    print(f'qtd  vinculados... {cont}')


cria_periodo_escolar()
vincula_periodo_escolar_a_escola()
