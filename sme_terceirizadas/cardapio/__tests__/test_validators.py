import pytest
from freezegun import freeze_time
from model_mommy import mommy
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..api.validators import (
    cardapio_antigo,
    data_troca_nao_pode_ser_superior_a_data_inversao,
    deve_ser_no_mesmo_ano_corrente,
    nao_pode_existir_solicitacao_igual_para_mesma_escola,
    nao_pode_ter_mais_que_60_dias_diferenca
)
from ..models import InversaoCardapio

pytestmark = pytest.mark.django_db


def test_valida_se_data_de_cardapio_eh_antiga(cardapio_valido, cardapio_invalido):
    assert cardapio_antigo(cardapio_valido)
    with pytest.raises(ValidationError, match='Não pode ser cardápio antigo'):
        cardapio_antigo(cardapio_invalido)


def test_valida_se_as_datas_se_convergem(cardapio_valido, cardapio_valido2):
    assert data_troca_nao_pode_ser_superior_a_data_inversao(cardapio_valido.data, cardapio_valido2.data)
    with pytest.raises(ValidationError, match='Data de cardápio para troca é superior a data de inversão'):
        data_troca_nao_pode_ser_superior_a_data_inversao(cardapio_valido2.data, cardapio_valido.data)


def test_valida_60_dias_exception(datas_de_inversoes_intervalo_maior_60_dias):
    data_de, data_para, esperado = datas_de_inversoes_intervalo_maior_60_dias
    with pytest.raises(serializers.ValidationError, match=esperado):
        nao_pode_ter_mais_que_60_dias_diferenca(data_de, data_para)


def test_valida_intervalo_menor_que_60_dias(datas_de_inversoes_intervalo_entre_60_dias):
    data_de, data_para, esperado = datas_de_inversoes_intervalo_entre_60_dias
    assert nao_pode_ter_mais_que_60_dias_diferenca(data_de, data_para) is esperado


def test_valida_ano_diferente_exception(data_inversao_ano_diferente):
    data_inversao, esperado = data_inversao_ano_diferente
    with pytest.raises(serializers.ValidationError, match=esperado):
        deve_ser_no_mesmo_ano_corrente(data_inversao)


@freeze_time('2019-07-10')
def test_valida_mesmo_ano(data_inversao_mesmo_ano):
    data_inversao, esperado = data_inversao_mesmo_ano
    assert deve_ser_no_mesmo_ano_corrente(data_inversao) is esperado


def test_nao_pode_existir_solicitacao_igual_para_mesma_escola_exceptio(datas_inversao_deste_mes, escola):
    data_de, data_para, _ = datas_inversao_deste_mes
    cardapio_de = mommy.make('Cardapio', data=data_de)
    cardapio_para = mommy.make('Cardapio', data=data_para)
    mommy.make(InversaoCardapio,
               cardapio_de=cardapio_de,
               cardapio_para=cardapio_para,
               status=InversaoCardapio.workflow_class.DRE_A_VALIDAR,
               escola=escola)
    with pytest.raises(ValidationError, match='Já existe uma solicitação de inversão com estes dados'):
        nao_pode_existir_solicitacao_igual_para_mesma_escola(data_de=data_de, data_para=data_para, escola=escola)
