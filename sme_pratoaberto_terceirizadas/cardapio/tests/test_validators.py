import pytest
from rest_framework.exceptions import ValidationError

# TODO: rodar o flake8 aqui
from ..api.validators import *


@pytest.mark.django_db
def test_valida_se_data_de_cardapio_eh_antiga(cardapio_valido, cardapio_invalido):
    assert cardapio_antigo(cardapio_valido)
    with pytest.raises(ValidationError, match='Não pode ser cardápio antigo'):
        cardapio_antigo(cardapio_invalido)


@pytest.mark.django_db
def test_valida_se_as_datas_se_convergem(cardapio_valido, cardapio_valido2):
    assert valida_cardapio_de_para(cardapio_valido.data, cardapio_valido2.data)
    with pytest.raises(ValidationError, match='Data de cardápio para troca é superior a data de inversão'):
        valida_cardapio_de_para(cardapio_valido2.data, cardapio_valido.data)
