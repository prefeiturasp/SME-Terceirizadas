from sme_terceirizadas.cardapio.data.motivos_alteracao_cardapio import data_motivoalteracaocardapio
from sme_terceirizadas.cardapio.data.motivos_suspensao_alimentacao import data_motivosuspensao
from sme_terceirizadas.cardapio.models import MotivoAlteracaoCardapio
from sme_terceirizadas.cardapio.models import MotivoSuspensao
from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import ja_existe


def cria_motivoalteracaocardapio():
    for item in data_motivoalteracaocardapio:
        _, created = MotivoAlteracaoCardapio.objects.get_or_create(nome=item)
        if not created:
            ja_existe('MotivoAlteracaoCardapio', item)


def cria_motivosuspensao():
    for item in data_motivosuspensao:
        _, created = MotivoSuspensao.objects.get_or_create(nome=item)
        if not created:
            ja_existe('MotivoSuspensao', item)
