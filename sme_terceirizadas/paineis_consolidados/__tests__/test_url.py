from rest_framework import status

from ..api.constants import AUTORIZADOS, CANCELADOS, NEGADOS, PENDENTES_AUTORIZACAO
from ...dados_comuns.constants import SEM_FILTRO


def base_codae(client_autenticado, resource):
    endpoint = f'/codae-solicitacoes/{resource}/'
    response = client_autenticado.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_painel_codae_pendentes_autorizacao(client_autenticado):
    base_codae(client_autenticado, f'{PENDENTES_AUTORIZACAO}/{SEM_FILTRO}')


def test_url_endpoint_painel_codae_aprovados(client_autenticado):
    base_codae(client_autenticado, AUTORIZADOS)


def test_url_endpoint_painel_codae_cancelados(client_autenticado):
    base_codae(client_autenticado, CANCELADOS)


def test_url_endpoint_painel_codae_negados(client_autenticado):
    base_codae(client_autenticado, NEGADOS)
