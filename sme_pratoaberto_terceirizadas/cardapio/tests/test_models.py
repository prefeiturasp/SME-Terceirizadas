import pytest

from ..models import (
    MotivoAlteracaoCardapio
)

pytestmark = pytest.mark.django_db


def test_motivo_alteracao_cardapio(motivo_alteracao_cardapio):
    assert motivo_alteracao_cardapio.nome is not None


