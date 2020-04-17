import time

import environ
import numpy as np
import pandas as pd

from sme_terceirizadas.produto.models import ProtocoloDeDietaEspecial
from sme_terceirizadas.perfil.models import Usuario

from utility.carga_dados.escola.helper import bcolors

ROOT_DIR = environ.Path(__file__) - 1

df = pd.read_excel(f'{ROOT_DIR}/planilhas/diagnosticos.xlsx',
                   converters={'NOME': str},
                   sheet_name='RELATORIO DIAGNOSTICO')

df = df.replace(np.nan, '', regex=True)

df['NOME'] = df['NOME'].str.strip().str.upper()


def percorre_data_frame_e_cria_patologia():
    usuario_codae = Usuario.objects.get(email='codae@admin.com')
    cont = 0
    for index, row in df.iterrows():
        nome = row['NOME']
        protocolo_obj, created = ProtocoloDeDietaEspecial.objects.get_or_create(
            nome=nome,
            criado_por=usuario_codae
        )
        if created:
            cont += 1
            print(f'<Protocolo> {protocolo_obj.nome} criado.')
    print(f'{bcolors.OKBLUE}Criados {cont} Protocolos de patologia...{bcolors.ENDC}')
    time.sleep(4)


percorre_data_frame_e_cria_patologia()
