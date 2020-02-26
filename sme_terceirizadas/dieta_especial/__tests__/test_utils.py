import pytest

from ..utils import dietas_especiais_a_terminar, termina_dietas_especiais


@pytest.mark.django_db
def test_dietas_especiais_a_terminar(solicitacoes_dieta_especial_com_data_termino):
    assert dietas_especiais_a_terminar().count() == 3


@pytest.mark.django_db
def test_termina_dietas_especiais(solicitacoes_dieta_especial_com_data_termino):
    termina_dietas_especiais()
    assert dietas_especiais_a_terminar().count() == 0
