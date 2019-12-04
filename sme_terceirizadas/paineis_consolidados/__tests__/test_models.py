import pytest

from ..models import SolicitacoesEscola

pytestmark = pytest.mark.django_db


def test_solicitacoes_escola(solicitacoes_escola_params):
    assert solicitacoes_escola_params.__len__() == 1
    solicitacoes_ano_corrente = SolicitacoesEscola.get_solicitacoes_ano_corrente()
    assert solicitacoes_ano_corrente.__len__() == 1
    assert list(solicitacoes_ano_corrente) == [{'data_evento__month': 10, 'desc_doc': 'Alteração de Cardápio'}]
