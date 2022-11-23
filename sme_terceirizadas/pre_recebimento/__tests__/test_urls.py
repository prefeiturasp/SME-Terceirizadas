import json

from rest_framework import status

from sme_terceirizadas.pre_recebimento.models import Cronograma, Laboratorio


def test_url_endpoint_cronograma(client_autenticado_dilog, armazem):
    data = {
        'armazem': armazem.uuid,
        'contrato_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
        'contrato': '5678/2022',
        'cadastro_finalizado': False,
        'etapas': [
            {
                'empenho_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
                'numero_empenho': '123456789'
            },
            {
                'empenho_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
                'numero_empenho': '1891425',
                'etapa': 'Etapa 1'
            }
        ],
        'programacoes_de_recebimento': [
            {
                'data_programada': '22/08/2022 - Etapa 1 - Parte 1',
                'tipo_carga': 'PALETIZADA'
            }
        ]
    }
    response = client_autenticado_dilog.post(
        '/cronogramas/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_201_CREATED
    obj = Cronograma.objects.last()
    assert obj.contrato == '5678/2022'


def test_url_lista_etapas_authorized_numeros(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/cronogramas/opcoes-etapas/')
    assert response.status_code == status.HTTP_200_OK


def test_url_list_cronogramas(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/cronogramas/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'count' in json
    assert 'next' in json
    assert 'previous' in json


def test_url_list_rascunhos_cronogramas(client_autenticado_dilog):
    response = client_autenticado_dilog.get('/cronogramas/rascunhos/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'results' in json


def test_url_endpoint_cronograma_editar(client_autenticado_dilog, cronograma_rascunho):
    data = {
        'contrato_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
        'contrato': '5678/2022',
        'cadastro_finalizado': True,
        'etapas': [
            {
                'empenho_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
                'numero_empenho': '123456789'
            },
            {
                'empenho_uuid': 'f1eb5ab9-fdb1-45ea-b43b-9da03f69f280',
                'numero_empenho': '1891425',
                'etapa': 'Etapa 1'
            }
        ],
        'programacoes_de_recebimento': [
            {
                'data_programada': '22/08/2022 - Etapa 1 - Parte 1',
                'tipo_carga': 'PALETIZADA'
            }
        ]
    }
    response = client_autenticado_dilog.put(
        f'/cronogramas/{cronograma_rascunho.uuid}/',
        content_type='application/json',
        data=json.dumps(data)
    )

    assert response.status_code == status.HTTP_200_OK
    obj = Cronograma.objects.last()
    assert cronograma_rascunho.contrato == '1234/2022'
    assert obj.contrato == '5678/2022'
    assert cronograma_rascunho.status == 'RASCUNHO'
    assert obj.status == 'ENVIADO_AO_FORNECEDOR'


def test_url_endpoint_laboratorio(client_autenticado_qualidade):
    data = {
        'contatos': [
            {
                'nome': 'TEREZA',
                'telefone': '8135431540',
                'email': 'maxlab@max.com',
            }
        ],
        'nome': 'LABORATORIO DE TESTES',
        'cnpj': '10359359000154',
        'cep': '53600000',
        'logradouro': 'OLIVEIR',
        'numero': '120',
        'complemento': '',
        'bairro': 'CENTRO',
        'cidade': 'IGARASSU',
        'estado': 'PE',
        'credenciado': True
    }
    response = client_autenticado_qualidade.post(
        '/laboratorios/',
        content_type='application/json',
        data=json.dumps(data)
    )
    assert response.status_code == status.HTTP_201_CREATED
    obj = Laboratorio.objects.last()
    assert obj.nome == 'LABORATORIO DE TESTES'


def test_url_lista_laboratorios_authorized(client_autenticado_qualidade):
    response = client_autenticado_qualidade.get('/laboratorios/')
    assert response.status_code == status.HTTP_200_OK
