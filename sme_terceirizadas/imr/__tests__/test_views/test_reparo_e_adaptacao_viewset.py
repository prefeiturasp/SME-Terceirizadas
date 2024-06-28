import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_reparo_e_adaptacao_por_edital(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    edital_factory,
    reparo_e_adaptacao_factory,
    edital_reparo_e_adaptacao_factory,
):
    client, usuario = client_autenticado_vinculo_coordenador_supervisao_nutricao

    edital = edital_factory.create(numero="78/SME/2016")
    reparo_e_adaptacao_1 = reparo_e_adaptacao_factory.create(nome="Armário")
    reparo_e_adaptacao_2 = reparo_e_adaptacao_factory.create(
        nome="Espelho protetor de tomada"
    )
    reparo_e_adaptacao_3 = reparo_e_adaptacao_factory.create(nome="Luminária")
    edital_reparo_e_adaptacao_factory.create(
        edital=edital,
        reparos_e_adaptacoes=(
            reparo_e_adaptacao_1,
            reparo_e_adaptacao_2,
            reparo_e_adaptacao_3,
        ),
    )

    response = client.get(f"/imr/reparos-e-adaptacoes/?edital_uuid={edital.uuid}")

    assert response.status_code == status.HTTP_200_OK

    results = response.json()["results"]
    assert len(results) == 3
    assert (
        any(insumo for insumo in results if insumo["nome"] == reparo_e_adaptacao_1.nome)
        is True
    )
    assert (
        any(insumo for insumo in results if insumo["nome"] == reparo_e_adaptacao_1.nome)
        is True
    )
    assert (
        any(insumo for insumo in results if insumo["nome"] == reparo_e_adaptacao_1.nome)
        is True
    )
