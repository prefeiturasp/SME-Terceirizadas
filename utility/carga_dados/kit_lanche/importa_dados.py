from random import sample
from utility.carga_dados.helper import ja_existe, progressbar

from sme_terceirizadas.kit_lanche.data.kit_lanche_item import data_kit_lanche_item
from sme_terceirizadas.kit_lanche.models import ItemKitLanche, KitLanche


def cria_kit_lanche_item():
    for item in progressbar(data_kit_lanche_item, 'Item Kit Lanche'):
        _, created = ItemKitLanche.objects.get_or_create(nome=item)
        if not created:
            ja_existe('ItemKitLanche', item)


def cria_kit_lanche():
    # Valores randomicos
    items = list(ItemKitLanche.objects.all())
    # Deleta kits existentes
    KitLanche.objects.all().delete()
    for i in progressbar(range(1, 11), 'Kit Lanche'):
        kit_amostra = sample(items, 3)
        kit_lanche = KitLanche.objects.create(nome=f'Kit {i}')
        for kit in kit_amostra:
            kit_lanche.itens.add(kit)
