import json

import pytest
from rest_framework import status

from sme_terceirizadas.terceirizada.models import Terceirizada

pytestmark = pytest.mark.django_db


def test_url_authorized_solicitacao(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/terceirizadas/')
    assert response.status_code == status.HTTP_200_OK


def test_post_empresa_distribuidor(client_autenticado_dilog, perfil_distribuidor):
    payload = {
        'nome_fantasia': 'Empresa Teste',
        'tipo_alimento': 'FLVO',
        'tipo_empresa': 'CONVENCIONAL',
        'tipo_servico': 'DISTRIBUIDOR_ARMAZEM',
        'numero_contrato': '89849',
        'razao_social': 'Empresa Teste SA',
        'cnpj': '65241564654645',
        'endereco': 'Rua teste',
        'cep': '04037000',
        'contatos': [
            {
                'nome': 'nome',
                'telefone': '0000000000000',
                'email': 'teste@gmail.com'
            }
        ],
        'bairro': 'Teste',
        'cidade': 'Teste',
        'complemento': 'Sim',
        'estado': 'SP',
        'numero': '58',
        'responsavel_cargo': 'Diretor',
        'responsavel_cpf': '68052799091',
        'responsavel_nome': 'Responsavel',
        'responsavel_telefone': '11999999999',
        'responsavel_email': 'responsavel@gmail.com',
        'lotes': [],
        'ativo': 'true',
        'contratos': [
            {
                'numero': '12345',
                'processo': '123',
                'vigencias': [
                    {
                        'data_inicial': '10/01/2023',
                        'data_final': '15/01/2023'
                    },
                ]
            }
        ],
        'super_admin': {
            'nome': 'xxx',
            'cpf': '00000000000',
            'email': 'xxx@xxx.com',
            'contatos': [
                {
                    'email': 'xxx@xxx.com',
                    'telefone': '000000000'
                }
            ]
        }
    }

    response = client_autenticado_dilog.post(
        '/empresas-nao-terceirizadas/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    empresa = Terceirizada.objects.first()

    assert response.status_code == status.HTTP_201_CREATED
    assert empresa.tipo_servico == Terceirizada.DISTRIBUIDOR_ARMAZEM


def test_url_endpoint_terceirizadas_actions(client_autenticado_dilog):

    client = client_autenticado_dilog

    response = client.get(f'/terceirizadas/lista-nomes/')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/terceirizadas/lista-nomes-distribuidores/')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/terceirizadas/lista-fornecedores-simples/')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/terceirizadas/lista-cnpjs/')
    assert response.status_code == status.HTTP_200_OK
