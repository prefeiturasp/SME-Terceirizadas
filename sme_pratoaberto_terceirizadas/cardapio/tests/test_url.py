from rest_framework import status


def test_url_endpoint_cardapio(client):
    response = client.get('/cardapios/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_endpoint_tipo_de_alimentacao(client):
    response = client.get('/tipos-alimentacao/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_endpoint_inverter_dia_cardapio(client):
    response = client.get('/inverte-dia-cardapio/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_endpoint_alteracoes_cardapio(client):
    response = client.get('/alteracoes-cardapio/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
