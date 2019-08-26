import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def base_get_request(client_autenticado, resource):
    endpoint = f'/{resource}/'
    response = client_autenticado.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_grupos_inclusao_alimentacao_normal(client_autenticado):
    base_get_request(client_autenticado, 'grupos-inclusao-alimentacao-normal')


def test_url_endpoint_grupos_inclusao_alimentacao_continua(client_autenticado):
    base_get_request(client_autenticado, 'inclusoes-alimentacao-continua')
