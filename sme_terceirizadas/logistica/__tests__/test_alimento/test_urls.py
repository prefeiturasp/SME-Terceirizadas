import json

import pytest
from django.conf import settings
from rest_framework import status

from ...models import UnidadeMedida
from ...utils import UnidadeMedidaPagination

pytestmark = pytest.mark.django_db


def test_url_unidades_medida_listar(client_autenticado, unidades_medida_logistica):
    """Deve acessar com sucesso a lista paginada de unidades de medida."""
    client = client_autenticado

    response = client.get('/unidades-medida-logistica/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == len(unidades_medida_logistica)
    assert len(response.data['results']) == UnidadeMedidaPagination.page_size
    assert response.data['next'] is not None


def test_url_unidades_medida_listar_com_filtros(client_autenticado):
    """Deve acessar com sucesso a lista paginada e filtrada de unidades de medida."""
    client = client_autenticado

    url_com_filtro_nome = '/unidades-medida-logistica/?nome=lit'
    response = client.get(url_com_filtro_nome)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['nome'] == 'LITRO'

    url_com_filtro_abreviacao = '/unidades-medida-logistica/?abreviacao=kg'
    response = client.get(url_com_filtro_abreviacao)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['nome'] == 'KILOGRAMA'

    url_com_filtro_sem_resultado = '/unidades-medida-logistica/?nome=lit&abreviacao=kg'
    response = client.get(url_com_filtro_sem_resultado)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0


def test_url_unidades_medida_detalhar(client_autenticado, unidade_medida_logistica):
    """Deve acessar com sucesso os detalhes de uma unidade de medida."""
    client = client_autenticado

    response = client.get(f'/unidades-medida-logistica/{unidade_medida_logistica.uuid}/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(unidade_medida_logistica.uuid)
    assert response.data['nome'] == str(unidade_medida_logistica.nome)
    assert response.data['abreviacao'] == str(unidade_medida_logistica.abreviacao)
    assert response.data['criado_em'] == unidade_medida_logistica.criado_em.strftime(
        settings.REST_FRAMEWORK['DATETIME_FORMAT'])


def test_url_unidades_medida_criar(client_autenticado):
    """Deve criar com sucesso uma unidade de medida."""
    client = client_autenticado
    payload = {
        'nome': 'UNIDADE MEDIDA TESTE',
        'abreviacao': 'umt'
    }

    response = client.post('/unidades-medida-logistica/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['nome'] == payload['nome']
    assert response.data['abreviacao'] == payload['abreviacao']
    assert UnidadeMedida.objects.filter(uuid=response.data['uuid']).exists()


def test_url_unidades_medida_criar_com_nome_invalido(client_autenticado):
    """Deve falhar ao tentar criar uma unidade de medida com atributo nome inválido (caixa baixa)."""
    client = client_autenticado
    payload = {
        'nome': 'unidade medida teste',
        'abreviacao': 'umt'
    }

    response = client.post('/unidades-medida-logistica/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data['nome'][0]) == 'O campo deve conter apenas letras maiúsculas.'


def test_url_unidades_medida_criar_com_abreviacao_invalida(client_autenticado):
    """Deve falhar ao tentar criar uma unidade de medida com atributo abreviacao inválida (caixa alta)."""
    client = client_autenticado
    payload = {
        'nome': 'UNIDADE MEDIDA TESTE',
        'abreviacao': 'UMT'
    }

    response = client.post('/unidades-medida-logistica/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data['abreviacao'][0]) == 'O campo deve conter apenas letras minúsculas.'


def test_url_unidades_medida_criar_repetida(client_autenticado, unidade_medida_logistica):
    """Deve falhar ao tentar criar uma unidade de medida que já esteja cadastrada."""
    client = client_autenticado
    payload = {
        'nome': 'UNIDADE TESTE',
        'abreviacao': 'ut'
    }

    response = client.post('/unidades-medida-logistica/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['non_field_errors'][0].code == 'unique'


def test_url_unidades_medida_atualizar(client_autenticado, unidade_medida_logistica):
    """Deve atualizar com sucesso uma unidade de medida."""
    client = client_autenticado
    payload = {
        'nome': 'UNIDADE MEDIDA TESTE ATUALIZADA',
        'abreviacao': 'umta'
    }

    response = client.patch(f'/unidades-medida-logistica/{unidade_medida_logistica.uuid}/', data=json.dumps(payload),
                            content_type='application/json')

    unidade_medida_logistica.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == unidade_medida_logistica.nome == payload['nome']
    assert response.data['abreviacao'] == unidade_medida_logistica.abreviacao == payload['abreviacao']
