import pytest

pytestmark = pytest.mark.django_db


def test_inversao_cardapio_serializer(inversao_cardapio_serializer):
    assert inversao_cardapio_serializer.data is not None


def test_suspensao_alimentacao_serializer(suspensao_alimentacao_serializer):
    assert suspensao_alimentacao_serializer.data is not None


def test_motivo_alteracao_cardapio_serializer(motivo_alteracao_cardapio_serializer):
    assert motivo_alteracao_cardapio_serializer.data is not None
    assert "nome" in motivo_alteracao_cardapio_serializer.data
    assert "uuid" in motivo_alteracao_cardapio_serializer.data


def test_alteracao_cardapio_serializer(alteracao_cardapio_serializer):
    assert alteracao_cardapio_serializer.data is not None
    assert "data_inicial" in alteracao_cardapio_serializer.data
    assert "data_final" in alteracao_cardapio_serializer.data
    assert "escola" in alteracao_cardapio_serializer.data


