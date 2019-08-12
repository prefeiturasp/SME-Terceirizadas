from rest_framework import status

def test_url_terceirizadas(client):
    response = client.get('/terceirizadas/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # TODO Criar um teste com autenticação
    assert str(response.content, encoding='utf8') == '{"detail":"As credenciais de autenticação não foram fornecidas."}'


def test_url_endpoint_editais(client):
    response = client.get('/editais/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # TODO Criar um teste com autenticação
    assert str(response.content, encoding='utf8') == '{"detail":"As credenciais de autenticação não foram fornecidas."}'


def test_url_endpoint_editais_contratos(client):
    response = client.get('/editais-contratos/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # TODO Criar um teste com autenticação
    assert str(response.content, encoding='utf8') == '{"detail":"As credenciais de autenticação não foram fornecidas."}'
