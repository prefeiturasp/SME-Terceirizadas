import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_usuarios(client_autenticado):
    response = client_autenticado.get('/usuarios/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    json = response.json()
    assert json['count'] == 1
    assert json['results'][0]['email'] == 'test@test.com'


def test_get_meus_dados(client_autenticado):
    response = client_autenticado.get('/usuarios/meus-dados/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    json = response.json()

    assert json['email'] == 'test@test.com'
    assert json['registro_funcional'] == '8888888'
    # assert json['tipo_usuario'] == 'indefinido'
    assert json['vinculo_atual'] == 'xxxx'


def test_post_usuarios(client_autenticado):
    response = client_autenticado.post('/usuarios/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    response = client_autenticado.put('/usuarios/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
