from freezegun import freeze_time
from rest_framework import status

from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow

ENRPOINT_INVERSOES = 'inversoes-dia-cardapio'


def test_url_endpoint_solicitacoes_inversao_inicio_fluxo(client_autenticado, inversao_dia_cardapio):
    assert str(inversao_dia_cardapio.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    assert str(json['uuid']) == str(inversao_dia_cardapio.uuid)


def test_url_endpoint_solicitacoes_inversao_dre_valida(client_autenticado, inversao_dia_cardapio_dre_validar):
    assert str(inversao_dia_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.DRE_VALIDA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validar.uuid)


def test_url_endpoint_solicitacoes_inversao_codae_autoriza(client_autenticado, inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.CODAE_AUTORIZA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validado.uuid)


def test_url_endpoint_solicitacoes_inversao_codae_nega(client_autenticado, inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.CODAE_NEGA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validado.uuid)


def test_url_endpoint_solicitacoes_inversao_codae_nega_error(client_autenticado, inversao_dia_cardapio_dre_validar):
    assert str(inversao_dia_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.CODAE_NEGA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'codae_nega' isn't available from state 'DRE_A_VALIDAR'."}


def test_url_endpoint_solicitacoes_inversao_terceirizada_ciencia(client_autenticado,
                                                                 inversao_dia_cardapio_codae_autorizado):
    assert str(inversao_dia_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_codae_autorizado.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
    assert str(json['uuid']) == str(inversao_dia_cardapio_codae_autorizado.uuid)


def test_url_endpoint_solicitacoes_inversao_terceirizada_ciencia_error(client_autenticado,
                                                                       inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'terceirizada_toma_ciencia' isn't available from state 'DRE_VALIDADO'."}


@freeze_time('2019-10-11')
def test_url_endpoint_solicitacoes_inversao_escola_cancela(client_autenticado,
                                                           inversao_dia_cardapio_codae_autorizado):
    assert str(inversao_dia_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_codae_autorizado.uuid}/{constants.ESCOLA_CANCELA}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU
    assert str(json['uuid']) == str(inversao_dia_cardapio_codae_autorizado.uuid)


@freeze_time('2019-12-31')
def test_url_endpoint_solicitacoes_inversao_escola_cancela_error(client_autenticado,
                                                                 inversao_dia_cardapio_codae_autorizado):
    assert str(inversao_dia_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_codae_autorizado.uuid}/{constants.ESCOLA_CANCELA}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': 'Erro de transição de estado: Só pode cancelar com no mínimo 2 dia(s) de antecedência'}
