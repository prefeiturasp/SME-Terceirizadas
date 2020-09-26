from sme_terceirizadas.cardapio.data.motivos_alteracao_cardapio import data
from sme_terceirizadas.cardapio.models import MotivoAlteracaoCardapio
from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import ja_existe


def cria_motivoalteracaocardapio():
    for item in data:
        obj, created = MotivoAlteracaoCardapio.objects.get_or_create(nome=item)
        if not created:
            ja_existe('MotivoAlteracaoCardapio', item)
