import pytest
from rest_framework import status

from sme_terceirizadas.logistica.models import Guia

pytestmark = pytest.mark.django_db


def test_url_authorized_numeros(client_autenticado_dilog, guia):
    response = client_autenticado_dilog.get('/guias-da-requisicao/lista-numeros/')
    assert response.status_code == status.HTTP_200_OK


def test_url_authorized_inconsistencias(client_autenticado_dilog, guia):
    response = client_autenticado_dilog.get('/guias-da-requisicao/inconsistencias/')
    assert response.status_code == status.HTTP_200_OK


def test_url_authorized_insucesso(client_autenticado_distribuidor, guia):
    response = client_autenticado_distribuidor.get('/guias-da-requisicao/lista-guias-para-insucesso/')
    assert response.status_code == status.HTTP_200_OK


def test_url_authorized_guias_escola(client_autenticado_escola_abastecimento, guia):
    response = client_autenticado_escola_abastecimento.get('/guias-da-requisicao/guias-escola/')
    assert response.status_code == status.HTTP_200_OK


def test_url_get_guia_conferencia_escola_invalida(client_autenticado_escola_abastecimento, guia):
    response = client_autenticado_escola_abastecimento.get(
        '/guias-da-requisicao/guia-para-conferencia/?uuid=' + str(guia.uuid)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_url_get_guia_conferencia_uuid_invalido(client_autenticado_escola_abastecimento, guia):
    # Sem UUID
    response = client_autenticado_escola_abastecimento.get('/guias-da-requisicao/guia-para-conferencia/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    # UUID inválido
    response = client_autenticado_escola_abastecimento.get('/guias-da-requisicao/guia-para-conferencia/?uuid=123')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    # UUID válido, porem sem guia
    response = client_autenticado_escola_abastecimento.get(
        '/guias-da-requisicao/guia-para-conferencia/?uuid=77316319-2645-493d-887d-55e40c3e74bb'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_url_get_guia_conferencia(client_autenticado_escola_abastecimento, guia_com_escola_client_autenticado):
    response = client_autenticado_escola_abastecimento.get(
        '/guias-da-requisicao/guia-para-conferencia/?uuid=' + str(guia_com_escola_client_autenticado.uuid)
    )
    assert Guia.objects.exists()
    assert Guia.objects.get(uuid=str(guia_com_escola_client_autenticado.uuid))
    assert response.status_code == status.HTTP_200_OK
