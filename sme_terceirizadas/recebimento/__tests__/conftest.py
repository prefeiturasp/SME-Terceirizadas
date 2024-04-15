import pytest

from sme_terceirizadas.dados_comuns.fluxo_status import FichaTecnicaDoProdutoWorkflow
from sme_terceirizadas.recebimento.models import QuestaoConferencia


@pytest.fixture
def questoes_conferencia(questao_conferencia_factory):
    return questao_conferencia_factory.create_batch(
        size=10,
        tipo_questao=[
            QuestaoConferencia.TIPO_QUESTAO_PRIMARIA,
            QuestaoConferencia.TIPO_QUESTAO_SECUNDARIA,
        ],
    )


@pytest.fixture
def payload_create_questoes_por_produto(
    ficha_tecnica_factory,
    questoes_conferencia,
):
    questoes = [str(q.uuid) for q in questoes_conferencia]

    return {
        "ficha_tecnica": str(
            ficha_tecnica_factory(status=FichaTecnicaDoProdutoWorkflow.APROVADA).uuid
        ),
        "questoes_primarias": questoes,
        "questoes_secundarias": questoes,
    }


@pytest.fixture
def payload_update_questoes_por_produto(questoes_conferencia):
    questoes = [str(q.uuid) for q in questoes_conferencia]

    return {
        "questoes_primarias": questoes,
        "questoes_secundarias": questoes,
    }
