import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized_solicitacao(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/solicitacao-remessa/')
    assert response.status_code == status.HTTP_200_OK


def test_url_authorized_numeros(client_autenticado_dilog, guia):
    response = client_autenticado_dilog.get('/solicitacao-remessa/lista-numeros/')
    assert response.status_code == status.HTTP_200_OK


def test_url_authorized_confirmadas(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/solicitacao-remessa/lista-requisicoes-confirmadas/')
    assert response.status_code == status.HTTP_200_OK
