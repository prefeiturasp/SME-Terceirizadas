from django.db.models import Q
from traitlets import Any

from sme_pratoaberto_terceirizadas.cardapio.models import Cardapio
from rest_framework import serializers
from datetime import date

from sme_pratoaberto_terceirizadas.escola.models import Escola
from ..models import InversaoCardapio


def cardapio_antigo(cardapio: Cardapio) -> Any:
    if cardapio.data <= date.today():
        raise serializers.ValidationError('Não pode ser cardápio antigo')
    return True


def valida_cardapio_de_para(cardapio_de: Cardapio, cardapio_para: Cardapio) -> Any:
    if cardapio_de.data >= cardapio_para.data:
        raise serializers.ValidationError('Data de cardápio para troca é superior a data de inversão')
    return True


def valida_duplicidade(cardapio_de: Cardapio, cardapio_para: Cardapio, escola: Escola) -> Any:
    inversao_cardapio = InversaoCardapio.objects.filter(cardapio_de=cardapio_de).filter(
        cardapio_para=cardapio_para).filter(
        escola=escola).exists()
    if inversao_cardapio:
        raise serializers.ValidationError('Já existe uma solicitação de inversão com estes dados')
    return True


def existe_data_cadastrada(cardapio_de: Cardapio, cardapio_para: Cardapio, escola: Escola):
    inversao_cardapio = InversaoCardapio.objects.filter(Q(cardapio_de=cardapio_de) | Q(cardapio_para=cardapio_para),
                                                        escola=escola).exists()
    if inversao_cardapio:
        return False
    return True
