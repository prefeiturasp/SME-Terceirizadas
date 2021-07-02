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


def test_url_exportar_excel_entregas_distribuidor(client_autenticado_distribuidor, solicitacao):
    response = client_autenticado_distribuidor.get(
        '/solicitacao-remessa/exporta-excel-visao-entregas/?uuid=' + str(solicitacao.uuid)
    )

    assert response.status_code == status.HTTP_200_OK


def test_url_exportar_excel_entregas_dilog(client_autenticado_dilog, solicitacao):
    response = client_autenticado_dilog.get(
        '/solicitacao-remessa/exporta-excel-visao-entregas/?uuid=' + str(solicitacao.uuid)
    )

    assert response.status_code == status.HTTP_200_OK


def test_url_excel_analitica_dilog(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/solicitacao-remessa/exporta-excel-visao-analitica/')
    assert response.status_code == status.HTTP_200_OK


def test_url_exportar_excel_analitica_distribuidor(client_autenticado_distribuidor):
    response = client_autenticado_distribuidor.get('/solicitacao-remessa/exporta-excel-visao-analitica/')
    assert response.status_code == status.HTTP_200_OK
