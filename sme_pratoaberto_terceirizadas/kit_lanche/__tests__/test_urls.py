import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def base_get_request(client_autenticado, resource):
    endpoint = f'/{resource}/'
    response = client_autenticado.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_kit_lanches(client_autenticado):
    base_get_request(client_autenticado, 'kit-lanches')


def test_url_endpoint_solicitacoes_kit_lanche_avulsa(client_autenticado):
    base_get_request(client_autenticado, 'solicitacoes-kit-lanche-avulsa')


def test_url_endpoint_solicitacoes_kit_lanche_unificada(client_autenticado):
    base_get_request(client_autenticado, 'solicitacoes-kit-lanche-unificada')
