from sme_terceirizadas.dados_comuns import constants
from sme_terceirizadas.dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow

ENRPOINT_INVERSOES = 'inversoes-dia-cardapio'


def test_url_endpoint_solicitacoes_inversao_inicio_fluxo(client_autenticado, inversao_dia_cardapio):
    assert str(inversao_dia_cardapio.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )

    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    assert str(json['uuid']) == str(inversao_dia_cardapio.uuid)


def test_url_endpoint_solicitacoes_inversao_dre_valida(client_autenticado, inversao_dia_cardapio_dre_validar):
    assert str(inversao_dia_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.DRE_VALIDA_PEDIDO}/'
    )

    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validar.uuid)


def test_url_endpoint_solicitacoes_inversao_codae_autoriza(client_autenticado, inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.CODAE_AUTORIZA_PEDIDO}/'
    )

    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validado.uuid)


def test_url_endpoint_solicitacoes_inversao_terceirizada_ciencia(client_autenticado,
                                                                 inversao_dia_cardapio_codae_autorizado):
    assert str(inversao_dia_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado.patch(
        f'/{ENRPOINT_INVERSOES}/{inversao_dia_cardapio_codae_autorizado.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )

    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
    assert str(json['uuid']) == str(inversao_dia_cardapio_codae_autorizado.uuid)
