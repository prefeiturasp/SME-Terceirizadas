import datetime

from django.db.models import Q
from rest_framework import serializers

from ...cardapio.models import (
    Cardapio,
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar,
    SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
)
from ...escola.models import Escola
from ..models import InversaoCardapio


def cardapio_antigo(cardapio: Cardapio):
    if cardapio.data <= datetime.date.today():
        raise serializers.ValidationError('Não pode ser cardápio antigo')
    return True


def data_troca_nao_pode_ser_superior_a_data_inversao(data_de: datetime.date, data_para: datetime.date):
    if data_de >= data_para:
        raise serializers.ValidationError(
            'Data da referência deve ser anterior a data aplicar em')
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
        raise serializers.ValidationError(
            'Já existe uma solicitação de inversão com estes dados')
    return True


def nao_pode_ter_mais_que_60_dias_diferenca(data_de: datetime.date, data_para: datetime.date):
    diferenca = abs((data_para - data_de).days)
    if diferenca > 60:
        raise serializers.ValidationError(
            'Diferença entre as datas não pode ultrapassar de 60 dias'
        )
    return True


def precisa_ter_combo(tipo_alimentacao_de: TipoAlimentacao,
                      tipo_alimentacao_para:
                      SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
                      vinculo: VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar):

    combo = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.filter(tipo_alimentacao=tipo_alimentacao_de,
                                                                      substituicao=tipo_alimentacao_para,
                                                                      vinculo=vinculo)
    if combo.count() == 0:
        raise serializers.ValidationError(
            f'Tipo de alimentação {tipo_alimentacao_para.label} não é substituível por {tipo_alimentacao_de.label}'

        )
    return True


def hora_inicio_nao_pode_ser_maior_que_hora_final(hora_inicial: datetime.time, hora_final: datetime.time):
    if hora_inicial >= hora_final:
        raise serializers.ValidationError(
            'Hora Inicio não pode ser maior do que hora final'
        )
    return True


def escola_nao_pode_cadastrar_dois_combos_iguais(escola: Escola, combo: ComboDoVinculoTipoAlimentacaoPeriodoTipoUE):
    """
    Se o combo de tipo de alimentacao já estiver cadastrado para a Escola, deverá retornar um erro.

    Pois para cada combo só é possivel registrar um intervalo de horario, caso o combo já estiver
    cadastrado, só será possivel atualizar o objeto HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar.
    """
    horario_combo_por_escola = HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar.objects.filter(
        escola=escola,
        combo_tipos_alimentacao=combo
    ).exists()
    if horario_combo_por_escola:
        raise serializers.ValidationError(
            'Já existe um horario registrado para esse combo nesta escola')
    return True
