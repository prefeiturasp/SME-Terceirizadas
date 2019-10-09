from rest_framework import status

from ..api.constants import AUTORIZADOS, CANCELADOS, NEGADOS, PENDENTES_APROVACAO
from ...dados_comuns.constants import SEM_FILTRO


def test_url_endpoint_painel_dre(client):
    response = client.get('/dre-pendentes-aprovacao/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_endpoint_painel_dre_autenticado(client_autenticado_painel_consolidados):
    client = client_autenticado_painel_consolidados
    response = client.get('/dre-pendentes-aprovacao/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def base_codae(client_autenticado, resource):
    endpoint = f'/codae-solicitacoes/{resource}/'
    response = client_autenticado.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_painel_codae_pendentes_aprovacao(client_autenticado):
    base_codae(client_autenticado, f'{PENDENTES_APROVACAO}/{SEM_FILTRO}')


def test_url_endpoint_painel_codae_aprovados(client_autenticado):
    base_codae(client_autenticado, AUTORIZADOS)


def test_url_endpoint_painel_codae_cancelados(client_autenticado):
    base_codae(client_autenticado, CANCELADOS)


def test_url_endpoint_painel_codae_negados(client_autenticado):
    base_codae(client_autenticado, NEGADOS)
