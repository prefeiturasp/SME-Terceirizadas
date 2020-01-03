import environ
import pandas as pd

from sme_terceirizadas.dieta_especial.models import AlergiaIntolerancia, ClassificacaoDieta, MotivoNegacao, TipoDieta

ROOT_DIR = environ.Path(__file__) - 1

def importa_alergias_intolerancias():
    df = pd.read_excel(f'{ROOT_DIR}/planilhas_de_carga/relacao_diagnostico.xlsx',
                    sheet_name='Relátorio Diagnóstico'
                    )

    for index, row in df.iterrows():
        print(f'AlergiaIntolerancia(descricao={row["Diagnóstico"]})')
        AlergiaIntolerancia.objects.create(descricao=row["Diagnóstico"])


def importa_motivos_negacao():
    df = pd.read_excel(f'{ROOT_DIR}/planilhas_de_carga/motivos_negacao.xlsx',
                    sheet_name='Planilha1'
                    )

    for index, row in df.iterrows():
        print(f'MotivoNegacao(descricao={row["Motivos"]})')
        MotivoNegacao.objects.create(descricao=row["Motivos"])


def cria_classificacoes_dieta():
    lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam congue nibh enim, ac vestibulum tortor semper vel. Integer dignissim libero in neque ultricies ullamcorper."
    classificacoes = [
        ['Tipo A', lorem],
        ['Tipo B', lorem],
        ['Tipo C', lorem],
    ]
    for nome, descricao in classificacoes:
        print(f'ClassificacaoDieta(nome={nome}, descricao={descricao})')
        ClassificacaoDieta.objects.create(nome=nome, descricao=descricao)


def cria_tipos_dieta():
    descricoes = [
        ['IL + Gluten (suco de fruta)'],
        ['Diabetes Mellitus'],
    ]
    for descricao in descricoes:
        print(f'TipoDieta(descricao={descricao})')
        TipoDieta.objects.create(descricao=descricao)


importa_alergias_intolerancias()
importa_motivos_negacao()
cria_classificacoes_dieta()
cria_tipos_dieta()
