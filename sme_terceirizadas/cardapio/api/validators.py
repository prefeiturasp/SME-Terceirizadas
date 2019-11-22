import datetime

from django.db.models import Q
from rest_framework import serializers

from ...cardapio.models import Cardapio, TipoAlimentacao
from ...escola.models import Escola
from ..models import InversaoCardapio


def cardapio_antigo(cardapio: Cardapio):
    if cardapio.data <= datetime.date.today():
        raise serializers.ValidationError('Não pode ser cardápio antigo')
    return True


def data_troca_nao_pode_ser_superior_a_data_inversao(data_de: datetime.date, data_para: datetime.date):
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


def precisa_pertencer_a_um_tipo_de_alimentacao(tipo_alimentacao_de: TipoAlimentacao,
                                               tipo_alimentacao_para: TipoAlimentacao):
    if tipo_alimentacao_para not in tipo_alimentacao_de.substituicoes.all():
        raise serializers.ValidationError(
            f'Tipo de alimentação {tipo_alimentacao_para.nome} não é substituível por {tipo_alimentacao_de.nome}'

        )
    return True
