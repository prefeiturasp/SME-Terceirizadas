import pytest
from rest_framework import status
from sme_terceirizadas.imr.models import PerfilDiretorSupervisao


pytestmark = pytest.mark.django_db


def test_tipos_ocorrencias(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    edital_factory,
    categoria_ocorrencia_factory,
    tipo_ocorrencia_factory
):

    edital = edital_factory.create()

    categoria = categoria_ocorrencia_factory.create(perfis=[PerfilDiretorSupervisao.SUPERVISAO])

    tipo_ocorrencia_factory.create(
        edital=edital,
        descricao='Ocorrencia 1',
        perfis=[PerfilDiretorSupervisao.SUPERVISAO],
        categoria=categoria
    )
    tipo_ocorrencia_factory.create(
        edital=edital,
        descricao='Ocorrencia 2',
        perfis=[PerfilDiretorSupervisao.SUPERVISAO],
        categoria=categoria
    )

    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid={edital.uuid}"
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert len(response_data) == 2
    assert response_data[0]['descricao'] == 'Ocorrencia 1'
    assert response_data[1]['descricao'] == 'Ocorrencia 2'

    client_autenticado_vinculo_coordenador_supervisao_nutricao.logout()


def test_tipos_ocorrencias_edital_UUID_invalido(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
):
    response = client_autenticado_vinculo_coordenador_supervisao_nutricao.get(
        f"/imr/formulario-supervisao/tipos-ocorrencias/?edital_uuid="
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    client_autenticado_vinculo_coordenador_supervisao_nutricao.logout()
