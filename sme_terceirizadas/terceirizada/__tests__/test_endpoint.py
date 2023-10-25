import json

import pytest
from rest_framework import status

from sme_terceirizadas.terceirizada.models import Terceirizada

pytestmark = pytest.mark.django_db


def test_url_authorized_solicitacao(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/terceirizadas/')
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_empresas_nao_terceirizadas_create(client_autenticado_dilog_cronograma):
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
                'ata': '1234',
                'pregao_chamada_publica': '12345',
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

    response = client_autenticado_dilog_cronograma.post(
        '/empresas-nao-terceirizadas/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    empresa = Terceirizada.objects.first()

    assert response.status_code == status.HTTP_201_CREATED
    assert empresa.tipo_servico == Terceirizada.DISTRIBUIDOR_ARMAZEM


def test_url_endpoint_empresas_nao_terceirizadas_cadastro_e_edicao_contratos(
    client_autenticado_dilog_cronograma, terceirizada
):
    payload = {
        'contratos': [
            {
                'encerrado': False,
                'numero': '1',
                'processo': '1',
                'ata': '1',
                'pregao_chamada_publica': '1',
                'vigencias': [
                    {
                        'data_inicial': '01/01/2023',
                        'data_final': '31/12/2023'
                    },
                ]
            },
            {
                'encerrado': False,
                'numero': '2',
                'processo': '2',
                'ata': '2',
                'pregao_chamada_publica': '2',
                'vigencias': [
                    {
                        'data_inicial': '01/01/2023',
                        'data_final': '31/12/2023'
                    },
                ]
            },
        ],
    }

    response = client_autenticado_dilog_cronograma.patch(
        f'/empresas-nao-terceirizadas/{terceirizada.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    terceirizada.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert terceirizada.contratos.count() == 2

    contrato_edicao = terceirizada.contratos.first()
    payload = {
        'contratos': [
            {
                'uuid': str(contrato_edicao.uuid),
                'encerrado': False,
                'numero': str(int(contrato_edicao.numero) + 1),
                'processo': '9',
                'ata': '9',
                'pregao_chamada_publica': '9',
                'vigencias': [
                    {
                        'data_inicial': '09/09/1999',
                        'data_final': '31/12/2023'
                    },
                ]
            },
        ],
    }

    response = client_autenticado_dilog_cronograma.patch(
        f'/empresas-nao-terceirizadas/{terceirizada.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    contrato_edicao.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK

    # numero não deve ser alterado ao se editar um contrato
    assert contrato_edicao.numero != payload['contratos'][0]['numero']

    assert contrato_edicao.processo == payload['contratos'][0]['processo']
    assert contrato_edicao.ata == payload['contratos'][0]['ata']
    assert contrato_edicao.pregao_chamada_publica == payload['contratos'][0]['pregao_chamada_publica']

    vigencia_contrato_edicao = contrato_edicao.vigencias.last()
    vigencia_payload = payload['contratos'][0]['vigencias'][0]
    assert vigencia_contrato_edicao.data_inicial.strftime('%d/%m/%Y') == vigencia_payload['data_inicial']
    assert vigencia_contrato_edicao.data_final.strftime('%d/%m/%Y') == vigencia_payload['data_final']


def test_url_endpoint_terceirizadas_actions(client_autenticado_dilog):

    client = client_autenticado_dilog

    response = client.get(f'/terceirizadas/lista-nomes/')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/terceirizadas/lista-nomes-distribuidores/')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/terceirizadas/lista-empresas-cronograma/')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/terceirizadas/lista-cnpjs/')
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_contratos_actions(client_autenticado_dilog_cronograma):
    client = client_autenticado_dilog_cronograma

    response = client.get(f'/contratos/numeros-contratos-cadastrados/')
    assert response.status_code == status.HTTP_200_OK
