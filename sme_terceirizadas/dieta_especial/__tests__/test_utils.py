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
    assert SolicitacaoDietaEspecial.objects.filter(
        status=DietaEspecialWorkflow.TERMINADA_AUTOMATICAMENTE_SISTEMA).count() == 3


@pytest.mark.django_db
def test_registrar_historico_criacao(protocolo_padrao_dieta_especial_2, substituicao_padrao_dieta_especial_2):
    from ..utils import log_create

    log_create(protocolo_padrao_dieta_especial_2)
    assert protocolo_padrao_dieta_especial_2.historico


@pytest.mark.django_db
def test_diff_protocolo_padrao(protocolo_padrao_dieta_especial_2, substituicao_padrao_dieta_especial_2):
    from ..utils import diff_protocolo_padrao
    validated_data = {
        'nome_protocolo': 'Alergia a manga',
        'orientacoes_gerais': 'Uma orientação',
        'status': 'I'
    }
    changes = diff_protocolo_padrao(protocolo_padrao_dieta_especial_2, validated_data)
    assert changes
