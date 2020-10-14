from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import ja_existe, progressbar

from sme_terceirizadas.dieta_especial.data.alimentos import data_alimentos
from sme_terceirizadas.dieta_especial.data.classificacao_dieta import data_classificacoes_dieta
from sme_terceirizadas.dieta_especial.data.alergia_intolerancia import data_alergia_intolerancias
from sme_terceirizadas.dieta_especial.data.motivo_negacao import data_motivo_negacoes
from sme_terceirizadas.dieta_especial.models import AlergiaIntolerancia, Alimento, ClassificacaoDieta, MotivoNegacao


def cria_alimento():
    for item in progressbar(data_alimentos, 'Alimento'):
        _, created = Alimento.objects.get_or_create(nome=item)
        if not created:
            ja_existe('Alimento', item)


def cria_motivo_negacao():
    for item in progressbar(data_motivo_negacoes, 'Motivo Negação'):
        _, created = MotivoNegacao.objects.get_or_create(descricao=item)
        if not created:
            ja_existe('MotivoNegacao', item)


def cria_classificacoes_dieta():
    for item in progressbar(data_classificacoes_dieta, 'Classificacao Dieta'):
        _, created = ClassificacaoDieta.objects.get_or_create(
            nome=item['nome'],
            descricao=item['descricao'],
        )
        if not created:
            ja_existe('ClassificacaoDieta', item)


def cria_alergia_intolerancias():
    for item in progressbar(data_alergia_intolerancias, 'Alergia Intolerancia'):  # noqa
        obj = AlergiaIntolerancia.objects.filter(descricao=item).first()
        if not obj:
            AlergiaIntolerancia.objects.create(descricao=item)
        else:
            nome = item
            print(f'{bcolors.FAIL}Aviso: AlergiaIntolerancia: "{nome}" já existe!{bcolors.ENDC}')  # noqa
