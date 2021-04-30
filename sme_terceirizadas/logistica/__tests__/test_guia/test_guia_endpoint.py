import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(client_autenticado_dilog, guia):
    response = client_autenticado_dilog.get('/guias-da-requisicao/inconsistencias/')
    assert response.status_code == status.HTTP_200_OK


def test_url_authorized_insucesso(client_autenticado_distribuidor, guia):
    response = client_autenticado_distribuidor.get('/guias-da-requisicao/lista-guias-para-insucesso/')
    assert response.status_code == status.HTTP_200_OK
