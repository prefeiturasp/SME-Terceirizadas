import pytest
from rest_framework.exceptions import ValidationError

# TODO: rodar o flake8 aqui
from ..api.validators import *
from ..models import SuspensaoAlimentacao


@pytest.mark.django_db
def test_valida_se_data_de_cardapio_eh_antiga(cardapio_valido, cardapio_invalido):
    assert cardapio_antigo(cardapio_valido)
    with pytest.raises(ValidationError, match='Não pode ser cardápio antigo'):
        cardapio_antigo(cardapio_invalido)


@pytest.mark.django_db
def test_valida_se_as_datas_se_convergem(cardapio_valido, cardapio_valido2):
    assert valida_cardapio_de_para(cardapio_valido, cardapio_valido2)
    with pytest.raises(ValidationError, match='Data de cardápio para troca é superior a data de inversão'):
        valida_cardapio_de_para(cardapio_valido2, cardapio_valido)


def test_valida_tipo_cardapio_inteiro():
    result = valida_tipo_cardapio_inteiro(
        cardapio='TEST',
        tipo=SuspensaoAlimentacao.CARDAPIO_INTEIRO,
        periodos=[],
        tipos_alimentacao=[]
    )
    assert result is True


def test_valida_tipo_cardapio_inteiro_exception():
    with pytest.raises(serializers.ValidationError,
                       match='Quando tipo 0'):
        valida_tipo_cardapio_inteiro(
            cardapio=None,
            tipo=SuspensaoAlimentacao.CARDAPIO_INTEIRO,
            periodos=[],
            tipos_alimentacao=[]
        )


def test_valida_tipo_periodo_escolar():
    result = valida_tipo_periodo_escolar(
        cardapio='',
        tipo=SuspensaoAlimentacao.PERIODO_ESCOLAR,
        periodos=['test', 'TEST'],
        tipos_alimentacao=[]
    )
    assert result is True


def test_valida_tipo_periodo_escolar_exception():
    with pytest.raises(serializers.ValidationError,
                       match='Quando tipo 1'):
        valida_tipo_periodo_escolar(
            cardapio='TEST',
            tipo=SuspensaoAlimentacao.PERIODO_ESCOLAR,
            periodos=[],
            tipos_alimentacao=['TEST']
        )


def test_valida_tipo_tipo_alimentacao():
    result = valida_tipo_alimentacao(
        cardapio='',
        tipo=SuspensaoAlimentacao.TIPO_ALIMENTACAO,
        periodos=[],
        tipos_alimentacao=['test', 'TEST']
    )
    assert result is True


def test_valida_tipo_tipo_alimentacao_exception():
    with pytest.raises(serializers.ValidationError,
                       match='Quando tipo 2'):
        valida_tipo_alimentacao(
            cardapio='TEST',
            tipo=SuspensaoAlimentacao.TIPO_ALIMENTACAO,
            periodos=['test', 'TEST'],
            tipos_alimentacao=['test', 'TEST']
        )
