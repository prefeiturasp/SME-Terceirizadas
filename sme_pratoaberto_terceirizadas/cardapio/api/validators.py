from datetime import date

from django.db.models import Q
from rest_framework import serializers
from traitlets import Any

from sme_pratoaberto_terceirizadas.cardapio.models import Cardapio, AlteracaoCardapio, TipoAlimentacao
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


def valida_duplicidade_alteracao_cardapio(tipo_de: TipoAlimentacao, tipo_para: TipoAlimentacao, escola: Escola) -> Any:
    alteracao_cardapio = AlteracaoCardapio.objects.filter(tipo_de=tipo_de).filter(
        tipo_para=tipo_para).filter(
        escola=escola).exists()
    if alteracao_cardapio:
        raise serializers.ValidationError('Já existe uma alteração de carvalho com estes dados')
    return True


def existe_data_cadastrada(cardapio_de: Cardapio, cardapio_para: Cardapio, escola: Escola):
    inversao_cardapio = InversaoCardapio.objects.filter(Q(cardapio_de=cardapio_de) | Q(cardapio_para=cardapio_para),
                                                        escola=escola).exists()
    if inversao_cardapio:
        return False
    return True


def valida_tipo_cardapio_inteiro(cardapio, periodos, tipo, tipos_alimentacao):
    if not cardapio:
        raise serializers.ValidationError(
            f'Quando tipo {tipo} (cardápio inteiro), deve ter cardápio')
    if periodos or tipos_alimentacao:
        raise serializers.ValidationError(
            f'Quando tipo {tipo} (cardápio inteiro), não pode ter períodos ou tipos de alimentação')
    return True


def valida_tipo_periodo_escolar(cardapio, periodos, tipo, tipos_alimentacao):
    if not periodos:
        raise serializers.ValidationError(
            f'Quando tipo {tipo} (periodo escolar), deve ter ao menos 1 periodo escolar')
    if cardapio or tipos_alimentacao:
        raise serializers.ValidationError(
            f'Quando tipo {tipo} (periodo escolar), não pode ter cardapio ou tipos de alimentação')
    return True


def valida_tipo_alimentacao(cardapio, periodos, tipo, tipos_alimentacao):
    if not tipos_alimentacao:
        raise serializers.ValidationError(
            f'Quando tipo {tipo} (tipo alimentação), deve ter ao menos 1 tipo de alimentação')
    if cardapio or periodos:
        raise serializers.ValidationError(
            f'Quando tipo {tipo} (tipo alimentação), não pode ter cardapio ou períodos')
    return True
