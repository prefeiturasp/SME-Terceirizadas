import pytest

from sme_terceirizadas.dados_comuns.fluxo_status import FichaTecnicaDoProdutoWorkflow
from sme_terceirizadas.recebimento.models import QuestaoConferencia


@pytest.fixture
def payload_questoes_por_produto(
    ficha_tecnica_factory,
    questao_conferencia_factory,
):
    questoes = [
        str(q.uuid)
        for q in questao_conferencia_factory.create_batch(
            size=10,
            tipo_questao=[
                QuestaoConferencia.TIPO_QUESTAO_PRIMARIA,
                QuestaoConferencia.TIPO_QUESTAO_SECUNDARIA,
            ],
            pergunta_obrigatoria=True,
        )
    ]

    return {
        "ficha_tecnica": str(
            ficha_tecnica_factory(status=FichaTecnicaDoProdutoWorkflow.APROVADA).uuid
        ),
        "questoes_primarias": questoes,
        "questoes_secundarias": questoes,
    }
