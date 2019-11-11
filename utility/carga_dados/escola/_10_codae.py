import environ
import numpy as np
import pandas as pd

from sme_terceirizadas.escola.models import DiretoriaRegional, Codae
from sme_terceirizadas.perfil.models import Perfil, Usuario
from utility.carga_dados.escola.helper import coloca_zero_a_esquerda
from .helper import cria_vinculo_de_perfil_usuario

ROOT_DIR = environ.Path(__file__) - 1

df = pd.read_excel(f'{ROOT_DIR}/planilhas_de_carga/CODAE_RF_CPF.xlsx',
                   converters={
                       'Nome': str,
                       'RF': str,
                       'CPF': str,
                       'Núcleo da CODAE': str
                   },
                   sheet_name='codae'
                   )

# tira os NAN e troca por espaco vazio ''
df = df.replace(np.nan, '', regex=True)

# padroniza os dados
df['Nome'] = df['Nome'].str.strip().str.upper()
df['CPF'] = df['CPF'].str.strip().str.upper()
df['RF'] = df['RF'].str.strip().str.upper()
df['Núcleo da CODAE'] = df['Núcleo da CODAE'].str.strip().str.upper()


def retorna_apenas_numeros_registro_funcional(registro_funcional):
    return registro_funcional.replace('.', '').replace('-', '')


def cria_usuario_gestor_alimentacao_ou_dieta_especial(registro_funcional, nome, cpf):
    email = f'{cpf}@emailteste.sme.prefeitura.sp.gov.br'
    usuario = Usuario.objects.create_user(email, registro_funcional)
    usuario.registro_funcional = retorna_apenas_numeros_registro_funcional(
        registro_funcional
    )
    usuario.nome = nome
    usuario.cpf = coloca_zero_a_esquerda(cpf, 11)
    usuario.is_active = False
    usuario.save()
    return usuario


def atribui_e_salva_cargos_a_codae(cargos):
    codae, created = Codae.objects.get_or_create(nome='CODAE')
    for cargo in cargos:
        cria_vinculo_de_perfil_usuario(
            cargo['perfil'],
            cargo['usuario'],
            codae
        )
        print(f'usuario: {cargo["usuario"].nome} foi criado e atribuido ao perfil CODAE: {cargo["perfil"].nome}')


def percorre_data_frame():
    gestao_alimentacao, created = Perfil.objects.get_or_create(
        nome='GESTAO_ALIMENTACAO_TERCEIRIZADA',
        ativo=True,
        super_usuario=True
    )
    dieta_especial, created = Perfil.objects.get_or_create(
        nome='DIETA_ESPECIAL',
        ativo=True,
        super_usuario=True
    )
    for index, row in df.iterrows():
        gestor_de_alimentacao_ou_dieta = cria_usuario_gestor_alimentacao_ou_dieta_especial(
            row['RF'],
            row['Nome'],
            row['CPF']
        )
        atribui_e_salva_cargos_a_codae(
            [
                {
                    'usuario': gestor_de_alimentacao_ou_dieta,
                    'perfil': dieta_especial if row['Núcleo da CODAE'] == 'DIETA ESPECIAL' else gestao_alimentacao
                },
            ]
        )


percorre_data_frame()
