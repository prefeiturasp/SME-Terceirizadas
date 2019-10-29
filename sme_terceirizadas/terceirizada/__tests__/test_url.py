from rest_framework import status


def test_url_terceirizadas_autenticado(client_autenticado_terceiro):
    client = client_autenticado_terceiro
    response = client.get('/terceirizadas/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['count'] == 1
    item = data['results'][0]

    assert isinstance(item, dict)
    assert len(item['nutricionistas']) == 1
    assert len(item['contatos']) == 1
    assert len(item['contratos']) == 1


def test_url_endpoint_editais_autenticado(client_autenticado_terceiro):
    client = client_autenticado_terceiro
    response = client.get('/editais/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['count'] == 1
    item = data['results'][0]

    assert isinstance(item, dict)


def test_url_endpoint_editais_contratos_autenticado(client_autenticado_terceiro):
    client = client_autenticado_terceiro
    response = client.get('/editais-contratos/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['count'] == 1
    item = data['results'][0]

    assert isinstance(item, dict)
    assert len(item['contratos']) == 1
