import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def base_request(client, django_user_model, resource):
    email = "test@test.com"
    password = "bar"
    django_user_model.objects.create_user(password=password, email=email)
    client.login(email=email, password=password)

    endpoint = f'/{resource}/'
    response = client.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_grupos_inclusao_alimentacao_normal(client, django_user_model):
    base_request(client, django_user_model, 'grupos-inclusao-alimentacao-normal')


def test_url_endpoint_grupos_inclusao_alimentacao_continua(client, django_user_model):
    base_request(client, django_user_model, 'inclusoes-alimentacao-continua')
