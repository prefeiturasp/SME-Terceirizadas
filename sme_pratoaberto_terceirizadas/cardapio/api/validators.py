from traitlets import Any

from sme_pratoaberto_terceirizadas.cardapio.models import Cardapio
from django.utils.timezone import now
from rest_framework import serializers


def cardapio_antigo(uuid_cardapio: str) -> Any:
    cardapio = Cardapio.objects.get(uuid=uuid_cardapio)
    if cardapio.data <= now():
        raise serializers.ValidationError('Não pode ser cardápio antigo')
    return True


def cardapio_existe(uuid_cardapio: str) -> Any:
    existe = Cardapio.objects.filter(uuid=uuid_cardapio).exists()
    if not existe:
        raise serializers.ValidationError('cardápio {} não existe'.format(uuid_cardapio))
    return True


def valida_cardapio_de_para(cardapio_de: Cardapio, cardapio_para: Cardapio) -> Any:
    if cardapio_de >= cardapio_para:
        raise serializers.ValidationError('Data de cardápio para troca é superior a data de inversão')
    return True
