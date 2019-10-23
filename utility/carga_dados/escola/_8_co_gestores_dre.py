import environ
import numpy as np
import pandas as pd

from sme_terceirizadas.perfil.models import GrupoPerfil, Perfil, Usuario
from sme_terceirizadas.escola.models import DiretoriaRegional

ROOT_DIR = environ.Path(__file__) - 1

df = pd.read_excel(f'{ROOT_DIR}/planilhas_de_carga/cogestores.xlsx',
                   converters={
                       'RF': str,
                       'RF-SUPLENTE': str,
                       'CPF-COGESTOR': str,
                       'CPF-SUPLENTE': str
                   },
                   sheet_name='cogestores'
                   )

# tira os NAN e troca por espaco vazio ''
df = df.replace(np.nan, '', regex=True)

# padroniza os dados
df['DRE'] = df['DRE'].str.strip().str.upper()
df['COGESTOR'] = df['COGESTOR'].str.strip().str.upper()
df['RF'] = df['RF'].str.strip().str.upper()
df['CPF-COGESTOR'] = df['CPF-COGESTOR'].str.strip().str.upper()
df['E-MAIL'] = df['E-MAIL'].str.strip()
df['SUPLENTE'] = df['SUPLENTE'].str.strip().str.upper()
df['RF-SUPLENTE'] = df['RF-SUPLENTE'].str.strip().str.upper()
df['CPF-SUPLENTE'] = df['CPF-SUPLENTE'].str.strip().str.upper()
df['E-MAIL-SUPLENTE'] = df['E-MAIL-SUPLENTE'].str.strip()


def busca_diretoria_regional(dre):
    try:
        return DiretoriaRegional.objects.get(iniciais__icontains=dre)
    except DiretoriaRegional.DoesNotExist:
        return None


def retorna_apenas_numeros_registro_funcional(registro_funcional):
    return registro_funcional.replace('.', '').replace('-', '')


def cria_usuario_gestor_ou_suplente(registro_funcional, nome, email, cpf, perfil_usuario):
    if nome == 'SEM SUPLENTE':
        return None
    else:
        usuario = Usuario.objects.create_user(email, registro_funcional)
        usuario.registro_funcional = retorna_apenas_numeros_registro_funcional(
            registro_funcional
        )
        usuario.nome = nome
        usuario.cpf = cpf
        usuario.is_active = False
        usuario.perfis.add(perfil_usuario)
        usuario.save()
        return usuario


def atribui_e_salva_usuarios_a_dre(dre, usuarios):
    for usuario in usuarios:
        if usuario is not None:
            dre.usuarios.add(usuario)
            print(f'usuario: {usuario.nome} foi criado e atribuido a DRE: {dre.nome}')
    dre.save()


def percorre_data_frame():
    grupo_dre = GrupoPerfil(
        nome='DIRETORIA REGIONAL',
        ativo=True
    )
    grupo_dre.save()
    perfil_gestor = Perfil(
        nome='CO-GESTOR',
        ativo=True,
        grupo=grupo_dre
    )
    perfil_gestor.save()
    perfil_suplente = Perfil(
        nome='SUPLENTE',
        ativo=True,
        grupo=grupo_dre
    )
    perfil_suplente.save()
    for index, row in df.iterrows():
        dre = busca_diretoria_regional(row['DRE'])
        cogestor = cria_usuario_gestor_ou_suplente(
            row['RF'],
            row['COGESTOR'],
            row['E-MAIL'],
            row['CPF-COGESTOR'],
            perfil_gestor
        )
        suplente = cria_usuario_gestor_ou_suplente(
            row['RF-SUPLENTE'],
            row['SUPLENTE'],
            row['E-MAIL-SUPLENTE'],
            row['CPF-SUPLENTE'],
            perfil_suplente
        )
        atribui_e_salva_usuarios_a_dre(dre, [cogestor, suplente])


percorre_data_frame()
