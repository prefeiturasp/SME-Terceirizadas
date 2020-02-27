import pytest

from ...dados_comuns.fluxo_status import DietaEspecialWorkflow
from ..models import SolicitacaoDietaEspecial
from ..utils import dietas_especiais_a_terminar, termina_dietas_especiais


@pytest.mark.django_db
def test_dietas_especiais_a_terminar(solicitacoes_dieta_especial_com_data_termino):
    assert dietas_especiais_a_terminar().count() == 3


@pytest.mark.django_db
def test_termina_dietas_especiais(solicitacoes_dieta_especial_com_data_termino, usuario_admin):
    termina_dietas_especiais(usuario_admin)
    assert dietas_especiais_a_terminar().count() == 0
    assert SolicitacaoDietaEspecial.objects.filter(status=DietaEspecialWorkflow.TERMINADA).count() == 3
