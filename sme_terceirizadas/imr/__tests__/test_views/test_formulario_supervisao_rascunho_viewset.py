import json

import pytest
from rest_framework import status

from sme_terceirizadas.imr.models import (
    FormularioOcorrenciasBase,
    PerfilDiretorSupervisao,
)

pytestmark = pytest.mark.django_db


def test_formulario_supervisao(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    escola,
    tipo_ocorrencia_factory,
):
    tipo_ocorrencia_1 = tipo_ocorrencia_factory.create()
    tipo_ocorrencia_2 = tipo_ocorrencia_factory.create()

    payload = {
        "data": "2024-05-15",
        "escola": str(escola.uuid),
        "maior_frequencia_no_periodo": 6,
        "ocorrencias_nao_se_aplica": [
            {
                "tipo_ocorrencia": str(tipo_ocorrencia_1.uuid),
                "descricao": "Não se aplica",
            },
            {
                "tipo_ocorrencia": str(tipo_ocorrencia_2.uuid),
                "descricao": "Não se aplica v2",
            },
        ],
    }

    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.post(
        f"/imr/rascunho-formulario-supervisao/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    data = response.json()

    instance = FormularioOcorrenciasBase.objects.get(uuid=data["formulario_base"])

    assert response.status_code == status.HTTP_201_CREATED
    assert data["escola"] == str(escola.uuid)
    assert data["status"] == "EM_PREENCHIMENTO"
    assert data["maior_frequencia_no_periodo"] == 6
    assert instance.respostas_nao_se_aplica.count() == 2


def test_formulario_supervisao_tipo_ocorrencia_nao_existe(
    client_autenticado_vinculo_coordenador_supervisao_nutricao, escola
):
    payload = {
        "data": "2024-05-15",
        "escola": str(escola.uuid),
        "ocorrencias_nao_se_aplica": [
            {
                "tipo_ocorrencia": "2b7a2217-1743-4bcd-8879-cf8e16e34fa6",
                "descricao": "",
            },
        ],
    }
    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.post(
        f"/imr/rascunho-formulario-supervisao/",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "ocorrencias_nao_se_aplica": {
            "tipo_ocorrencia": [
                "Objeto com uuid=2b7a2217-1743-4bcd-8879-cf8e16e34fa6 não existe."
            ]
        }
    }


def test_tipos_ocorrencias(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    edital_factory,
    categoria_ocorrencia_factory,
    tipo_ocorrencia_factory,
):
    edital = edital_factory.create()

    categoria = categoria_ocorrencia_factory.create(
        perfis=[PerfilDiretorSupervisao.SUPERVISAO]
    )

    tipo_ocorrencia_factory.create(
        edital=edital,
        descricao="Ocorrencia 1",
        perfis=[PerfilDiretorSupervisao.SUPERVISAO],
        categoria=categoria,
        posicao=1,
    )
    tipo_ocorrencia_factory.create(
        edital=edital,
        descricao="Ocorrencia 2",
        perfis=[PerfilDiretorSupervisao.SUPERVISAO],
        categoria=categoria,
        posicao=2,
    )

    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid={edital.uuid}"
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert len(response_data) == 2
    assert response_data[0]["descricao"] == "Ocorrencia 1"
    assert response_data[1]["descricao"] == "Ocorrencia 2"

    client_autenticado_vinculo_coordenador_supervisao_nutricao.logout()


def test_tipos_ocorrencias_edital_UUID_invalido(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
):
    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid="
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    client_autenticado_vinculo_coordenador_supervisao_nutricao.logout()
