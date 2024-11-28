import pytest
from rest_framework import status

from sme_terceirizadas.escola.models import Lote, TipoUnidadeEscolar

pytestmark = pytest.mark.django_db


def test_list(
    client_autenticado_da_escola,
    kit_lanche_factory,
    escola,
    contrato_factory,
    edital_factory,
):
    edital = edital_factory.create(numero="78/SME/2016")
    edital_2 = edital_factory.create(numero="31/SME/2022")
    contrato_factory.create(
        edital=edital, terceirizada=escola.lote.terceirizada, lotes=Lote.objects.all()
    )
    kit_lanche_factory.create(
        edital=edital, tipos_unidades=TipoUnidadeEscolar.objects.all()
    )
    kit_lanche_factory.create(
        edital=edital_2, tipos_unidades=TipoUnidadeEscolar.objects.all()
    )

    response = client_autenticado_da_escola.get("/kit-lanches/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1


def test_list_escola_cemei(
    client_autenticado_da_escola,
    kit_lanche_factory,
    escola,
    contrato_factory,
    edital_factory,
    tipo_unidade_escolar_factory,
):
    escola.tipo_unidade.iniciais = "CEMEI"
    escola.tipo_unidade.save()
    tipo_unidade_cei_diret = tipo_unidade_escolar_factory.create(iniciais="CEI DIRET")

    edital = edital_factory.create(numero="78/SME/2016")
    edital_2 = edital_factory.create(numero="31/SME/2022")
    contrato_factory.create(
        edital=edital, terceirizada=escola.lote.terceirizada, lotes=Lote.objects.all()
    )
    kit_lanche_factory.create(
        edital=edital,
        tipos_unidades=TipoUnidadeEscolar.objects.filter(id=tipo_unidade_cei_diret.id),
    )
    kit_lanche_factory.create(
        edital=edital_2, tipos_unidades=TipoUnidadeEscolar.objects.all()
    )

    response = client_autenticado_da_escola.get("/kit-lanches/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
