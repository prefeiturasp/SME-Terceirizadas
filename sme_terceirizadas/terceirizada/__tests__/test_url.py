import json

from rest_framework import status


def test_url_terceirizadas_autenticado(client_autenticado_terceiro):
    client = client_autenticado_terceiro
    response = client.get('/terceirizadas/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['count'] == 1
    item = data['results'][0]

    assert isinstance(item, dict)
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


def test_cadastro_empresa(users_codae_gestao_alimentacao):
    client, email, password, rf, cpf, user = users_codae_gestao_alimentacao
    data = {
        'nutricionistas': [
            {'nome': 'Yolanda', 'crn_numero': '0987654', 'super_admin_terceirizadas': True,
             'contatos': [
                 {
                     'telefone': '12 32131 2312', 'email': 'yolanda@empresa.teste.com'
                 }
             ]
             }
        ],
        'nome_fantasia': 'Empresa Empresada', 'razao_social': 'Empresa LTDA', 'cnpj': '58833199000119',
        'representante_legal': 'Seu Carlos', 'representante_telefone': '12 12212 1121',
        'representante_email': 'carlos@empresa.teste.com', 'endereco': 'Rua dos Coqueiros 123', 'cep': '09123456',
        'contatos': [{'telefone': '12 12121 2121', 'email': 'empresa@empresa.teste.com'}],
        'lotes': ['143c2550-8bf0-46b4-b001-27965cfcd107']}
    response = client.post('/terceirizadas/', content_type='application/json', data=json.dumps(data))
    assert response.status_code == status.HTTP_201_CREATED
    terceirizada_uuid = response.json()['uuid']
    data_update = {
        'nutricionistas': [
            {'nome': 'Yolanda', 'crn_numero': '0987654', 'super_admin_terceirizadas': False,
             'contatos': [
                 {
                     'telefone': '12 32131 2312', 'email': 'yolanda@empresa.teste.com'
                 }
             ]}, {
                'nome': 'Yago', 'crn_numero': '7654321', 'super_admin_terceirizadas': True,
                'contatos': [
                    {
                        'telefone': '11 32334 2212', 'email': 'yago@empresa.teste.com'
                    }
                ]
            }
        ],
        'nome_fantasia': 'Empresa Empresada', 'razao_social': 'Empresa LTDA', 'cnpj': '58833199000119',
        'representante_legal': 'Seu Carlos', 'representante_telefone': '12 12212 1121',
        'representante_email': 'carlos@empresa.teste.com', 'endereco': 'Rua dos Coqueiros 123', 'cep': '09123456',
        'contatos': [{'telefone': '12 12121 2121', 'email': 'empresa@empresa.teste.com'}],
        'lotes': ['143c2550-8bf0-46b4-b001-27965cfcd107']}
    response = client.put(f'/terceirizadas/{terceirizada_uuid}/', content_type='application/json',
                          data=json.dumps(data_update))
    assert response.status_code == status.HTTP_200_OK
