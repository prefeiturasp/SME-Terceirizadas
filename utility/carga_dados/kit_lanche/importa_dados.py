from sme_terceirizadas.kit_lanche.data.kit_lanche_item import data_kit_lanche_item
from sme_terceirizadas.kit_lanche.data.kit_lanche import data_kit_lanche
from sme_terceirizadas.kit_lanche.models import ItemKitLanche
from sme_terceirizadas.kit_lanche.models import KitLanche
from utility.carga_dados.helper import ja_existe


def cria_kit_lanche_item():
    for item in data_kit_lanche_item:
        _, created = ItemKitLanche.objects.get_or_create(nome=item)
        if not created:
            ja_existe('ItemKitLanche', item)


def cria_kit_lanche():
    pass
