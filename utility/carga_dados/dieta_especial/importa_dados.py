from utility.carga_dados.helper import ja_existe, progressbar

from sme_terceirizadas.dieta_especial.data.motivo_negacao import data_motivo_negacoes
from sme_terceirizadas.dieta_especial.models import MotivoNegacao


def cria_motivo_negacao():
    for item in progressbar(data_motivo_negacoes, 'Motivo Negação'):
        _, created = MotivoNegacao.objects.get_or_create(descricao=item)
        if not created:
            ja_existe('MotivoNegacao', item)
