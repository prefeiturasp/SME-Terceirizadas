import datetime

from django.db.models import Q
from rest_framework import serializers
from traitlets import Any

from sme_pratoaberto_terceirizadas.cardapio.models import Cardapio
from sme_pratoaberto_terceirizadas.escola.models import Escola
from ..models import InversaoCardapio


def cardapio_antigo(cardapio: Cardapio) -> Any:
    if cardapio.data <= datetime.date.today():
        raise serializers.ValidationError('Não pode ser cardápio antigo')
    return True


def data_troca_nao_pode_ser_superior_a_data_inversao(data_de: datetime.date, data_para: datetime.date) -> Any:
    if data_de >= data_para:
        raise serializers.ValidationError('Data de cardápio para troca é superior a data de inversão')
    return True


def nao_pode_existir_solicitacao_igual_para_mesma_escola(data_de: datetime.date, data_para: datetime.date,
                                                         escola: Escola):
    inversao_cardapio = InversaoCardapio.objects.filter(
        cardapio_de__data=data_de,
        cardapio_para__data=data_para,
        escola=escola).filter(
        ~Q(status=InversaoCardapio.workflow_class.RASCUNHO)
    ).exists()
    if inversao_cardapio:
        raise serializers.ValidationError('Já existe uma solicitação de inversão com estes dados')
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


def deve_ser_no_mesmo_ano_corrente(data_inversao: datetime.date):
    ano_corrente = datetime.date.today().year
    if ano_corrente != data_inversao.year:
        raise serializers.ValidationError(
            'Inversão de dia de cardapio deve ser solicitada no ano corrente'
        )
    return True


def nao_pode_ter_mais_que_60_dias_diferenca(data_de: datetime.date, data_para: datetime.date):
    diferenca = abs((data_para - data_de).days)
    if diferenca > 60:
        raise serializers.ValidationError(
            'Diferença entre as datas não pode ultrapassar de 60 dias'
        )
    return True
