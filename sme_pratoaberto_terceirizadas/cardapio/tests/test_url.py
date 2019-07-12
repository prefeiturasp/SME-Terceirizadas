from rest_framework import status


def test_url_endpoint_cardapio(client):
    response = client.get('/cardapio/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_endpoint_tipo_de_alimentacao(client):
    response = client.get('/tipo-alimentacao/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
