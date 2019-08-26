from rest_framework import status


# TODO Encontrar forma de testar com autenticação no JWT
def test_url_endpoint_painel_dre(client):
    response = client.get('/dre-pendentes-aprovacao/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
