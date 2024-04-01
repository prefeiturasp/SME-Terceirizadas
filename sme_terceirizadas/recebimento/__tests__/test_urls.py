import json

from faker import Faker
from rest_framework import status

from sme_terceirizadas.recebimento.models import QuestaoConferencia, QuestoesPorProduto

fake = Faker("pt_BR")


def test_url_questoes_conferencia_list(
    client_autenticado_qualidade,
    questao_conferencia_factory,
):
    questoes_criadas = questao_conferencia_factory.create_batch(
        size=10,
        tipo_questao=[
            QuestaoConferencia.TIPO_QUESTAO_PRIMARIA,
            QuestaoConferencia.TIPO_QUESTAO_SECUNDARIA,
        ],
        pergunta_obrigatoria=True,
    ) + questao_conferencia_factory.create_batch(
        size=10,
        tipo_questao=[
            QuestaoConferencia.TIPO_QUESTAO_PRIMARIA,
            QuestaoConferencia.TIPO_QUESTAO_SECUNDARIA,
        ],
        posicao=None,
    )

    response = client_autenticado_qualidade.get("/questoes-conferencia/")
    questoes_primarias = response.json()["results"]["primarias"]
    questoes_secundarias = response.json()["results"]["secundarias"]
    total_questoes = QuestaoConferencia.objects.count()

    assert response.status_code == status.HTTP_200_OK
    assert total_questoes == len(questoes_criadas)
    for questoes in [questoes_primarias, questoes_secundarias]:
        assert _questoes_ordenadas(questoes)


def _questoes_ordenadas(questoes):
    return all(
        questoes[i].get("posicao") <= questoes[i + 1].get("posicao")
        for i in range(len(questoes) - 1)
        if questoes[i].get("posicao") and questoes[i + 1].get("posicao")
    )


def test_url_questoes_por_produto_create(
    client_autenticado_qualidade,
    payload_questoes_por_produto,
):
    response = client_autenticado_qualidade.post(
        "/questoes-por-produto/",
        content_type="application/json",
        data=json.dumps(payload_questoes_por_produto),
    )

    questoes_por_produto = QuestoesPorProduto.objects.first()

    assert response.status_code == status.HTTP_201_CREATED
    assert questoes_por_produto is not None
    assert questoes_por_produto.questoes_primarias.count() == len(
        payload_questoes_por_produto["questoes_primarias"]
    )
    assert questoes_por_produto.questoes_secundarias.count() == len(
        payload_questoes_por_produto["questoes_secundarias"]
    )
