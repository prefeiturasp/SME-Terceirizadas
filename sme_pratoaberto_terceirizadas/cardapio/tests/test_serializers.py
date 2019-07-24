import pytest

pytestmark = pytest.mark.django_db


def test_inversao_cardapio_serializer(inversao_cardapio_serializer):
    assert inversao_cardapio_serializer.data is not None


def test_suspensao_alimentacao_serializer(suspensao_alimentacao_serializer):
    assert suspensao_alimentacao_serializer.data is not None
