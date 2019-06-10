import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_view_acesso_sem_token(client):
    response = client.get('/refeicao/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# def test_view_com_token(client, token):
#     client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
#     response = client.get('/refeicao/')
#     assert response.status_code == status.HTTP_200_OK
