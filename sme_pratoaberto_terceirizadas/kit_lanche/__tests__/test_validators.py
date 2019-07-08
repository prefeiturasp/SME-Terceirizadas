import pytest
from rest_framework.exceptions import ValidationError

from ..validators import (
    valida_tempo_passeio_lista_igual,
    escola_quantidade_deve_ter_mesmo_tempo_passeio,
    escola_quantidade_deve_ter_1_ou_mais_kits,
    escola_quantidade_deve_ter_0_kit, solicitacao_deve_ter_0_kit,
    solicitacao_deve_ter_1_ou_mais_kits
)
from ..validators import (valida_tempo_passeio_lista_nao_igual)


def test_valida_tempo_passeio_lista_nao_igual():
    assert valida_tempo_passeio_lista_nao_igual(None) is True


def test_valida_tempo_passeio_lista_nao_igual_exception():
    with pytest.raises(ValidationError, match='tempo de passeio deve ser null'):
        valida_tempo_passeio_lista_nao_igual(1)


def test_valida_tempo_passeio_lista_igual(horarios_passeio):
    tempo, esperado = horarios_passeio
    assert valida_tempo_passeio_lista_igual(tempo) is esperado


def test_horarios_passeio_invalido(horarios_passeio_invalido):
    tempo, esperado = horarios_passeio_invalido
    with pytest.raises(ValidationError, match=esperado):
        valida_tempo_passeio_lista_igual(tempo)


def test_escola_quantidade_deve_ter_mesmo_tempo_passeio():
    escola_quantidade_mock = {'tempo_passeio': 3}
    dado_base_mock = {'tempo_passeio': 3}
    assert escola_quantidade_deve_ter_mesmo_tempo_passeio(
        escola_quantidade_mock,
        dado_base_mock, 3) is True


def test_escola_quantidade_deve_ter_mesmo_tempo_passeio_exception():
    escola_quantidade_mock = {'tempo_passeio': 4}
    dado_base_mock = {'tempo_passeio': 3}
    esperado = 'escola_quantidade indice #3 diverge do ' \
               'tempo_passeio de dado_base.'
    with pytest.raises(ValidationError, match=esperado):
        escola_quantidade_deve_ter_mesmo_tempo_passeio(
            escola_quantidade=escola_quantidade_mock,
            dado_base=dado_base_mock,
            indice=3)


def test_escola_quantidade_deve_ter_1_ou_mais_kits():
    assert escola_quantidade_deve_ter_1_ou_mais_kits(3, 2) is True


def test_escola_quantidade_deve_ter_1_ou_mais_kits_exception():
    esperado = 'escola_quantidade indice # 2 deve ter 1 ou mais kits'
    with pytest.raises(ValidationError, match=esperado):
        escola_quantidade_deve_ter_1_ou_mais_kits(0, 2)


def test_escola_quantidade_deve_ter_0_kit():
    assert escola_quantidade_deve_ter_0_kit(0, 3) is True


def test_escola_quantidade_deve_ter_0_kit_exception():
    esperado = 'escola_quantidade indice # 3 deve ter 0 kit'
    with pytest.raises(ValidationError, match=esperado):
        escola_quantidade_deve_ter_0_kit(1, 3)


def test_solicitacao_deve_ter_0_kit():
    assert solicitacao_deve_ter_0_kit(0) is True


def test_solicitacao_deve_ter_0_kit_exception():
    esperado = 'Em "dado_base", quando lista_kit_lanche NÃO é igual, deve ter 0 kit'
    with pytest.raises(ValidationError, match=esperado):
        solicitacao_deve_ter_0_kit(1)


def test_solicitacao_deve_ter_1_ou_mais_kits():
    assert solicitacao_deve_ter_1_ou_mais_kits(numero_kits=3) is True


def test_solicitacao_deve_ter_1_ou_mais_kits_exception():
    esperado = 'Quando lista_kit_lanche_igual é Verdadeiro, "dado_base", deve ter de 1 a 3 kits'
    with pytest.raises(ValidationError, match=esperado):
        solicitacao_deve_ter_1_ou_mais_kits(numero_kits=0)
