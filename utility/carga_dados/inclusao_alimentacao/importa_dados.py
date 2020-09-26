from sme_terceirizadas.inclusao_alimentacao.data.motivo_inclusao_continua import data_motivo_inclusao_continua
from sme_terceirizadas.inclusao_alimentacao.data.motivo_inclusao_normal import data_motivo_inclusao_normal
from sme_terceirizadas.inclusao_alimentacao.models import MotivoInclusaoContinua
from sme_terceirizadas.inclusao_alimentacao.models import MotivoInclusaoNormal
from utility.carga_dados.helper import ja_existe


def cria_motivo_inclusao_continua():
    for item in data_motivo_inclusao_continua:
        _, created = MotivoInclusaoContinua.objects.get_or_create(nome=item)
        if not created:
            ja_existe('MotivoInclusaoContinua', item)


def cria_motivo_inclusao_normal():
    for item in data_motivo_inclusao_normal:
        _, created = MotivoInclusaoNormal.objects.get_or_create(nome=item)
        if not created:
            ja_existe('MotivoInclusaoNormal', item)
