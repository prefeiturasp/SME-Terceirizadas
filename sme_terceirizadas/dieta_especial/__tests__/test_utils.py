import pytest

from ..utils import dietas_especiais_a_expirar, expira_dietas_especiais


@pytest.mark.django_db
def test_dietas_especiais_a_expirar(solicitacoes_dieta_especial_com_data_expiracao):
    assert dietas_especiais_a_expirar().count() == 3


@pytest.mark.django_db
def test_expira_dietas_especiais(solicitacoes_dieta_especial_com_data_expiracao):
    expira_dietas_especiais()
    assert dietas_especiais_a_expirar().count() == 0
