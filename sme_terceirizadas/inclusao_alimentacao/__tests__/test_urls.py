import pytest
from rest_framework import status

from ...dados_comuns.constants import (
    CODAE_AUTORIZA_PEDIDO,
    CODAE_NEGA_PEDIDO,
    DRE_INICIO_PEDIDO,
    DRE_NAO_VALIDA_PEDIDO,
    DRE_VALIDA_PEDIDO,
    TERCEIRIZADA_TOMOU_CIENCIA
)
from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow

pytestmark = pytest.mark.django_db


def base_get_request(client_autenticado, resource):
    endpoint = f'/{resource}/'
    response = client_autenticado.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_grupos_inclusao_alimentacao_normal(client_autenticado):
    base_get_request(client_autenticado, 'grupos-inclusao-alimentacao-normal')


def test_url_endpoint_grupos_inclusao_alimentacao_continua(client_autenticado):
    base_get_request(client_autenticado, 'inclusoes-alimentacao-continua')


def test_url_endpoint_grupos_inclusao_motivos_inclusao_normal(client_autenticado):
    base_get_request(client_autenticado, 'motivos-inclusao-normal')


def test_url_endpoint_grupos_inclusao_motivos_inclusao_continua(client_autenticado):
    base_get_request(client_autenticado, 'motivos-inclusao-continua')


def test_url_endpoint_inclusao_continua_inicio(client_autenticado, inclusao_alimentacao_continua):
    assert inclusao_alimentacao_continua.status == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado.patch(
        f'/inclusoes-alimentacao-continua/{inclusao_alimentacao_continua.uuid}/{DRE_INICIO_PEDIDO}/')
    assert response.status_code == 200
    assert response.json()['status'] == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR


def test_url_endpoint_inclusao_continua_dre_valida(client_autenticado, inclusao_alimentacao_continua_dre_validar):
    assert inclusao_alimentacao_continua_dre_validar.status == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado.patch(
        f'/inclusoes-alimentacao-continua/{inclusao_alimentacao_continua_dre_validar.uuid}/{DRE_VALIDA_PEDIDO}/')
    assert response.status_code == 200
    assert response.json()['status'] == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO


def test_url_endpoint_inclusao_continua_dre_nao_valida(client_autenticado, inclusao_alimentacao_continua_dre_validar):
    assert inclusao_alimentacao_continua_dre_validar.status == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado.patch(
        f'/inclusoes-alimentacao-continua/{inclusao_alimentacao_continua_dre_validar.uuid}/{DRE_NAO_VALIDA_PEDIDO}/')
    assert response.status_code == 200
    assert response.json()['status'] == PedidoAPartirDaEscolaWorkflow.DRE_NAO_VALIDOU_PEDIDO_ESCOLA


def test_url_endpoint_inclusao_continua_codae_autoriza(client_autenticado, inclusao_alimentacao_continua_dre_validado):
    assert inclusao_alimentacao_continua_dre_validado.status == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado.patch(
        f'/inclusoes-alimentacao-continua/{inclusao_alimentacao_continua_dre_validado.uuid}/{CODAE_AUTORIZA_PEDIDO}/')
    assert response.status_code == 200
    assert response.json()['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO


def test_url_endpoint_inclusao_continua_codae_nega(client_autenticado, inclusao_alimentacao_continua_dre_validado):
    assert inclusao_alimentacao_continua_dre_validado.status == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado.patch(
        f'/inclusoes-alimentacao-continua/{inclusao_alimentacao_continua_dre_validado.uuid}/{CODAE_NEGA_PEDIDO}/')
    assert response.status_code == 200
    assert response.json()['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO


def test_url_endpoint_inclusao_continua_terc_ciencia(client_autenticado,
                                                     inclusao_alimentacao_continua_codae_autorizado):
    assert inclusao_alimentacao_continua_codae_autorizado.status == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado.patch(
        f'/inclusoes-alimentacao-continua/{inclusao_alimentacao_continua_codae_autorizado.uuid}/'
        f'{TERCEIRIZADA_TOMOU_CIENCIA}/')
    assert response.status_code == 200
    assert response.json()['status'] == PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
