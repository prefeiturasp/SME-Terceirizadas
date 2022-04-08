import datetime
import json
import random

from freezegun import freeze_time
from rest_framework import status

from sme_terceirizadas.cardapio.models import AlteracaoCardapio, GrupoSuspensaoAlimentacao, InversaoCardapio

from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import InformativoPartindoDaEscolaWorkflow, PedidoAPartirDaEscolaWorkflow

ENDPOINT_INVERSOES = 'inversoes-dia-cardapio'
ENDPOINT_SUSPENSOES = 'grupos-suspensoes-alimentacao'
ENDPOINT_SUSPENSOES_DE_CEI = 'suspensao-alimentacao-de-cei'
ENDPOINT_ALTERACAO_CARD = 'alteracoes-cardapio'
ENDPOINT_ALTERACAO_CARD_CEI = 'alteracoes-cardapio-cei'
ENDPOINT_VINCULOS_ALIMENTACAO = 'vinculos-tipo-alimentacao-u-e-periodo-escolar'
ENDPOINT_HORARIO_DO_COMBO = 'horario-do-combo-tipo-de-alimentacao-por-unidade-escolar'

ESCOLA_INFORMA_SUSPENSAO = 'informa-suspensao'


#
# Inversão de dia de Cardápio
#
def daqui_dez_dias_ou_ultimo_dia_do_ano():
    hoje = datetime.date.today()
    dia_alteracao = hoje + datetime.timedelta(days=10)
    if dia_alteracao.year != hoje.year:
        dia_alteracao = datetime.date(hoje.year, 12, 31)
    return dia_alteracao


def test_permissoes_inversao_cardapio_viewset(client_autenticado_vinculo_escola_cardapio,
                                              inversao_dia_cardapio,
                                              inversao_dia_cardapio_outra_dre):
    # pode ver os dados de uma alteração de cardápio da mesma escola
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio.uuid}/'
    )
    assert response.status_code == status.HTTP_200_OK
    # Não pode ver dados de uma inversão de dia de cardápio de outra escola
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_outra_dre.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    # não pode ver os dados de TODAS as inversões de dia de cardápio
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_INVERSOES}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Você não tem permissão para executar essa ação.'}
    # pode deletar somente se for escola e se estiver como rascunho
    inversao_dia_cardapio.status = PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    inversao_dia_cardapio.save()
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Você só pode excluir quando o status for RASCUNHO.'}
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_outra_dre.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    inversao_dia_cardapio.status = PedidoAPartirDaEscolaWorkflow.RASCUNHO
    inversao_dia_cardapio.save()
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio.uuid}/'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_url_endpoint_inversao_minhas_solicitacoes(client_autenticado_vinculo_escola_cardapio):
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_INVERSOES}/{constants.SOLICITACOES_DO_USUARIO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 1


def test_url_endpoint_solicitacoes_inversao_inicio_fluxo(client_autenticado_vinculo_escola_cardapio,
                                                         inversao_dia_cardapio):
    assert str(inversao_dia_cardapio.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    assert str(json['uuid']) == str(inversao_dia_cardapio.uuid)


def test_url_endpoint_solicitacoes_inversao_relatorio(client_autenticado,
                                                      inversao_dia_cardapio):
    response = client_autenticado.get(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio.uuid}/{constants.RELATORIO}/'
    )
    id_externo = inversao_dia_cardapio.id_externo
    assert response.status_code == status.HTTP_200_OK
    assert response._headers['content-type'] == ('Content-Type', 'application/pdf')
    assert response._headers['content-disposition'] == (
        'Content-Disposition', f'filename="solicitacao_inversao_{id_externo}.pdf"')
    assert 'PDF-1.5' in str(response.content)
    assert isinstance(response.content, bytes)


def test_url_endpoint_solicitacoes_inversao_inicio_fluxo_error(client_autenticado_vinculo_escola_cardapio,
                                                               inversao_dia_cardapio_dre_validar):
    assert str(inversao_dia_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'inicia_fluxo' isn't available from state 'DRE_A_VALIDAR'."}


def test_url_endpoint_solicitacoes_inversao_dre_valida(client_autenticado_vinculo_dre_cardapio,
                                                       inversao_dia_cardapio_dre_validar):
    assert str(inversao_dia_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.DRE_VALIDA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validar.uuid)


def test_url_endpoint_solicitacoes_inversao_dre_valida_error(client_autenticado_vinculo_dre_cardapio,
                                                             inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.DRE_VALIDA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'dre_valida' isn't available from state 'DRE_VALIDADO'."}


def test_url_endpoint_solicitacoes_inversao_dre_nao_valida(client_autenticado_vinculo_dre_cardapio,
                                                           inversao_dia_cardapio_dre_validar):
    assert str(inversao_dia_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.DRE_NAO_VALIDA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_NAO_VALIDOU_PEDIDO_ESCOLA
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validar.uuid)
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.DRE_NAO_VALIDA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'dre_nao_valida' isn't available from state "
                  "'DRE_NAO_VALIDOU_PEDIDO_ESCOLA'."}


def test_url_endpoint_solicitacoes_inversao_codae_autoriza_403(client_autenticado_vinculo_codae_dieta_cardapio,
                                                               inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_codae_dieta_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.CODAE_AUTORIZA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_url_endpoint_solicitacoes_inversao_codae_autoriza(client_autenticado_vinculo_codae_cardapio,
                                                           inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.CODAE_AUTORIZA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validado.uuid)


def test_url_endpoint_solicitacoes_inversao_codae_autoriza_error(client_autenticado_vinculo_codae_cardapio,
                                                                 inversao_dia_cardapio_dre_validar):
    assert str(inversao_dia_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.CODAE_AUTORIZA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'codae_autoriza_questionamento' "
                  "isn't available from state 'DRE_A_VALIDAR'."}


def test_url_endpoint_solicitacoes_inversao_codae_nega(client_autenticado_vinculo_codae_cardapio,
                                                       inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.CODAE_NEGA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validado.uuid)


def test_url_endpoint_solicitacoes_inversao_codae_nega_error(client_autenticado_vinculo_codae_cardapio,
                                                             inversao_dia_cardapio_dre_validar):
    assert str(inversao_dia_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validar.uuid}/{constants.CODAE_NEGA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'codae_nega_questionamento'"
                  " isn't available from state 'DRE_A_VALIDAR'."}


def test_url_endpoint_solicitacoes_inversao_codae_questiona(client_autenticado_vinculo_codae_cardapio,
                                                            inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.CODAE_QUESTIONA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO
    assert str(json['uuid']) == str(inversao_dia_cardapio_dre_validado.uuid)


def test_url_endpoint_solicitacoes_inversao_codae_questiona_error(client_autenticado_vinculo_codae_cardapio,
                                                                  inversao_dia_cardapio_codae_autorizado):
    assert str(inversao_dia_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_codae_autorizado.uuid}/{constants.CODAE_QUESTIONA_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail':
            "Erro de transição de estado: Transition 'codae_questiona' isn't available from state 'CODAE_AUTORIZADO'."
    }


def test_url_endpoint_solicitacoes_inversao_terceirizada_responde_questionamento(
    client_autenticado_vinculo_terceirizada_cardapio,
    inversao_dia_cardapio_codae_questionado
):
    justificativa = 'TESTE JUSTIFICATIVA'
    resposta = True
    assert str(inversao_dia_cardapio_codae_questionado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/'
        f'{inversao_dia_cardapio_codae_questionado.uuid}/'
        f'{constants.TERCEIRIZADA_RESPONDE_QUESTIONAMENTO}/',
        data={'justificativa': justificativa, 'resposta_sim_nao': resposta}
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO
    assert json['logs'][0]['justificativa'] == justificativa
    assert json['logs'][0]['resposta_sim_nao'] == resposta
    assert str(json['uuid']) == str(inversao_dia_cardapio_codae_questionado.uuid)
    assert str(inversao_dia_cardapio_codae_questionado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/'
        f'{inversao_dia_cardapio_codae_questionado.uuid}/'
        f'{constants.TERCEIRIZADA_RESPONDE_QUESTIONAMENTO}/',
        data={'justificativa': justificativa, 'resposta_sim_nao': resposta}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail':
            "Erro de transição de estado: Transition 'terceirizada_responde_questionamento' isn't available from state "
            "'TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO'."
    }


def test_url_endpoint_solicitacoes_inversao_terceirizada_ciencia(client_autenticado_vinculo_terceirizada_cardapio,
                                                                 inversao_dia_cardapio_codae_autorizado):
    assert str(inversao_dia_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_codae_autorizado.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
    assert str(json['uuid']) == str(inversao_dia_cardapio_codae_autorizado.uuid)


def test_url_endpoint_solicitacoes_inversao_terceirizada_ciencia_error(client_autenticado_vinculo_terceirizada_cardapio,
                                                                       inversao_dia_cardapio_dre_validado):
    assert str(inversao_dia_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_dre_validado.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'terceirizada_toma_ciencia' "
                  "isn't available from state 'DRE_VALIDADO'."}


@freeze_time('2019-10-11')
def test_url_endpoint_solicitacoes_inversao_escola_cancela(client_autenticado_vinculo_escola_cardapio,
                                                           inversao_dia_cardapio_codae_autorizado):
    assert str(inversao_dia_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_codae_autorizado.uuid}/{constants.ESCOLA_CANCELA}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU
    assert str(json['uuid']) == str(inversao_dia_cardapio_codae_autorizado.uuid)


@freeze_time('2019-12-31')
def test_url_endpoint_solicitacoes_inversao_escola_cancela_error(client_autenticado_vinculo_escola_cardapio,
                                                                 inversao_dia_cardapio_codae_autorizado):
    assert str(inversao_dia_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_INVERSOES}/{inversao_dia_cardapio_codae_autorizado.uuid}/{constants.ESCOLA_CANCELA}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': 'Erro de transição de estado: Só pode cancelar com no mínimo 2 dia(s) de antecedência'}


#
# Suspensão de alimentação
#

def test_permissoes_suspensao_alimentacao_cei_viewset(client_autenticado_vinculo_escola_cardapio,
                                                      suspensao_alimentacao_de_cei):
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_SUSPENSOES_DE_CEI}/{suspensao_alimentacao_de_cei.uuid}/'
    )
    assert response.status_code == status.HTTP_200_OK

    suspensao_alimentacao_de_cei.status = InformativoPartindoDaEscolaWorkflow.INFORMADO
    suspensao_alimentacao_de_cei.save()
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_SUSPENSOES_DE_CEI}/{suspensao_alimentacao_de_cei.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Você só pode excluir quando o status for RASCUNHO.'}

    suspensao_alimentacao_de_cei.status = PedidoAPartirDaEscolaWorkflow.RASCUNHO
    suspensao_alimentacao_de_cei.save()

    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_SUSPENSOES_DE_CEI}/{suspensao_alimentacao_de_cei.uuid}/{ESCOLA_INFORMA_SUSPENSAO}/')
    assert response.status_code == status.HTTP_200_OK

    suspensao_alimentacao_de_cei.status = PedidoAPartirDaEscolaWorkflow.RASCUNHO
    suspensao_alimentacao_de_cei.save()
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_SUSPENSOES_DE_CEI}/{suspensao_alimentacao_de_cei.uuid}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_permissoes_suspensao_alimentacao_viewset(client_autenticado_vinculo_escola_cardapio,
                                                  grupo_suspensao_alimentacao,
                                                  grupo_suspensao_alimentacao_outra_dre):
    # pode ver os dados de uma suspensão de alimentação da mesma escola
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao.uuid}/'
    )
    assert response.status_code == status.HTTP_200_OK
    # Não pode ver dados de uma suspensão de alimentação de outra escola
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao_outra_dre.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    # não pode ver os dados de TODAS as suspensões de alimentação
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_SUSPENSOES}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Você não tem permissão para executar essa ação.'}
    grupo_suspensao_alimentacao.status = InformativoPartindoDaEscolaWorkflow.INFORMADO
    grupo_suspensao_alimentacao.save()
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Você só pode excluir quando o status for RASCUNHO.'}
    # pode deletar somente se for escola e se estiver como rascunho
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao_outra_dre.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    grupo_suspensao_alimentacao.status = PedidoAPartirDaEscolaWorkflow.RASCUNHO
    grupo_suspensao_alimentacao.save()
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao.uuid}/'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_url_endpoint_suspensao_minhas_solicitacoes(client_autenticado_vinculo_escola_cardapio):
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_SUSPENSOES}/meus_rascunhos/'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 1


def test_url_endpoint_suspensoes_informa(client_autenticado_vinculo_escola_cardapio, grupo_suspensao_alimentacao):
    assert str(grupo_suspensao_alimentacao.status) == InformativoPartindoDaEscolaWorkflow.RASCUNHO
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao.uuid}/{constants.ESCOLA_INFORMA_SUSPENSAO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == InformativoPartindoDaEscolaWorkflow.INFORMADO
    assert str(json['uuid']) == str(grupo_suspensao_alimentacao.uuid)


def test_url_endpoint_suspensoes_informa_error(client_autenticado_vinculo_escola_cardapio,
                                               grupo_suspensao_alimentacao_informado):
    assert str(grupo_suspensao_alimentacao_informado.status) == InformativoPartindoDaEscolaWorkflow.INFORMADO
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao_informado.uuid}/{constants.ESCOLA_INFORMA_SUSPENSAO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Erro de transição de estado: Transition 'informa' "
                                         "isn't available from state 'INFORMADO'."}


def test_url_endpoint_suspensoes_relatorio(client_autenticado,
                                           grupo_suspensao_alimentacao_informado):
    response = client_autenticado.get(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao_informado.uuid}/{constants.RELATORIO}/'
    )
    id_externo = grupo_suspensao_alimentacao_informado.id_externo
    assert response.status_code == status.HTTP_200_OK
    assert response._headers['content-type'] == ('Content-Type', 'application/pdf')
    assert response._headers['content-disposition'] == (
        'Content-Disposition', f'filename="solicitacao_suspensao_{id_externo}.pdf"')
    assert 'PDF-1.5' in str(response.content)
    assert isinstance(response.content, bytes)


def test_url_endpoint_suspensoes_terc_ciencia(client_autenticado_vinculo_terceirizada_cardapio,
                                              grupo_suspensao_alimentacao_informado):
    assert str(grupo_suspensao_alimentacao_informado.status) == InformativoPartindoDaEscolaWorkflow.INFORMADO
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao_informado.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == InformativoPartindoDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
    assert str(json['uuid']) == str(grupo_suspensao_alimentacao_informado.uuid)


def test_url_endpoint_suspensoes_terc_ciencia_error(client_autenticado_vinculo_terceirizada_cardapio,
                                                    grupo_suspensao_alimentacao):
    assert str(grupo_suspensao_alimentacao.status) == InformativoPartindoDaEscolaWorkflow.RASCUNHO
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_SUSPENSOES}/{grupo_suspensao_alimentacao.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Erro de transição de estado: Transition 'terceirizada_toma_ciencia'"
                                         " isn't available from state 'RASCUNHO'."}


#
# Alteração de cardápio
#

def test_permissoes_alteracao_cardapio_viewset(client_autenticado_vinculo_escola_cardapio,
                                               alteracao_cardapio,
                                               alteracao_cardapio_outra_dre):
    # pode ver os dados de uma alteração de cardápio da mesma escola
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/'
    )
    assert response.status_code == status.HTTP_200_OK
    # Não pode ver dados de uma alteração de cardápio de outra escola
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_outra_dre.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    # não pode ver os dados de TODAS as alterações de cardápio
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_ALTERACAO_CARD}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Você não tem permissão para executar essa ação.'}
    alteracao_cardapio.status = PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    alteracao_cardapio.save()
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Você só pode excluir quando o status for RASCUNHO.'}
    # pode deletar somente se for escola e se estiver como rascunho
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_outra_dre.uuid}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    alteracao_cardapio.status = PedidoAPartirDaEscolaWorkflow.RASCUNHO
    alteracao_cardapio.save()
    response = client_autenticado_vinculo_escola_cardapio.delete(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_url_endpoint_alteracao_minhas_solicitacoes(client_autenticado_vinculo_escola_cardapio):
    response = client_autenticado_vinculo_escola_cardapio.get(
        f'/{ENDPOINT_ALTERACAO_CARD}/{constants.SOLICITACOES_DO_USUARIO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 1


def test_url_endpoint_alt_card_inicio_403(client_autenticado_vinculo_dre_cardapio,
                                          alteracao_cardapio):
    assert str(alteracao_cardapio.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    # somente escola pode iniciar fluxo
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Você não tem permissão para executar essa ação.'}


def test_url_endpoint_alt_card_criar(client_autenticado_vinculo_escola_cardapio, motivo_alteracao_cardapio, escola,
                                     tipo_alimentacao, alteracao_substituicoes_params, periodo_escolar):
    hoje = datetime.date.today()
    if hoje.month == 12 and hoje.day == 30:
        return
    dia_alteracao = daqui_dez_dias_ou_ultimo_dia_do_ano()
    (data_inicial, data_final, combo1, combo2, substituicao1, substituicao2) = alteracao_substituicoes_params
    data = {
        'motivo': str(motivo_alteracao_cardapio.uuid),
        'alterar_dia': dia_alteracao.isoformat(),
        'data_inicial': dia_alteracao.isoformat(),
        'data_final': dia_alteracao.isoformat(),
        'escola': escola.uuid,
        'substituicoes': [{
            'periodo_escolar': str(periodo_escolar.uuid),
            'tipo_alimentacao_de': str(combo1.uuid),
            'tipo_alimentacao_para': str(substituicao1.uuid),
            'qtd_alunos': 10
        }]
    }

    response = client_autenticado_vinculo_escola_cardapio.post(f'/{ENDPOINT_ALTERACAO_CARD}/',
                                                               content_type='application/json',
                                                               data=json.dumps(data))
    assert response.status_code == status.HTTP_201_CREATED
    resp_json = response.json()

    dia_alteracao_formatada = dia_alteracao.strftime('%d/%m/%Y')
    assert resp_json['data_inicial'] == dia_alteracao_formatada
    assert resp_json['data_final'] == dia_alteracao_formatada

    assert resp_json['status_explicacao'] == 'RASCUNHO'
    assert resp_json['escola'] == escola.uuid
    assert resp_json['motivo'] == str(motivo_alteracao_cardapio.uuid)

    substituicao = resp_json['substituicoes'][0]
    assert substituicao['periodo_escolar'] == str(periodo_escolar.uuid)
    assert substituicao['tipo_alimentacao_de'] == str(combo1.uuid)
    assert substituicao['tipo_alimentacao_para'] == str(substituicao1.uuid)
    assert substituicao['qtd_alunos'] == 10


def test_url_endpoint_alt_card_cei_criar(client_autenticado_vinculo_escola_cardapio, motivo_alteracao_cardapio, escola,
                                         tipo_alimentacao, alteracao_substituicoes_params, periodo_escolar,
                                         faixas_etarias_ativas):
    hoje = datetime.date.today()
    if hoje.month == 12 and hoje.day == 30:
        return
    dia_alteracao = daqui_dez_dias_ou_ultimo_dia_do_ano()
    (data_inicial, data_final, combo1, combo2, substituicao1, substituicao2) = alteracao_substituicoes_params
    data = {
        'motivo': str(motivo_alteracao_cardapio.uuid),
        'data': dia_alteracao.isoformat(),
        'escola': escola.uuid,
        'observacao': 'Alteração por causa do feriado',
        'substituicoes': [{
            'periodo_escolar': str(periodo_escolar.uuid),
            'tipo_alimentacao_de': str(combo1.uuid),
            'tipo_alimentacao_para': str(substituicao1.uuid),
            'faixas_etarias': [{
                'faixa_etaria': str(fe.uuid),
                'quantidade': random.randint(0, 50)
            } for fe in faixas_etarias_ativas]
        }]
    }

    response = client_autenticado_vinculo_escola_cardapio.post(f'/{ENDPOINT_ALTERACAO_CARD_CEI}/',
                                                               content_type='application/json',
                                                               data=json.dumps(data))
    assert response.status_code == status.HTTP_201_CREATED
    resp_json = response.json()

    assert resp_json['data'] == dia_alteracao.strftime('%d/%m/%Y')
    assert resp_json['status_explicacao'] == 'RASCUNHO'
    assert resp_json['escola'] == escola.uuid
    assert resp_json['motivo'] == str(motivo_alteracao_cardapio.uuid)
    assert resp_json['observacao'] == 'Alteração por causa do feriado'

    substituicao = resp_json['substituicoes'][0]
    assert substituicao['periodo_escolar'] == str(periodo_escolar.uuid)
    assert substituicao['tipo_alimentacao_de'] == str(combo1.uuid)
    assert substituicao['tipo_alimentacao_para'] == str(substituicao1.uuid)

    for [enviado, recebido] in zip(data['substituicoes'][0]['faixas_etarias'],
                                   resp_json['substituicoes'][0]['faixas_etarias']):
        assert enviado['faixa_etaria'] == recebido['faixa_etaria']
        assert enviado['quantidade'] == recebido['quantidade']


def test_url_endpoint_alt_card_inicio(client_autenticado_vinculo_escola_cardapio,
                                      alteracao_cardapio):
    assert str(alteracao_cardapio.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    assert str(json['uuid']) == str(alteracao_cardapio.uuid)


def test_url_endpoint_alt_card_cei_inicio(client_autenticado_vinculo_escola_cardapio,
                                          alteracao_cardapio_cei):
    assert str(alteracao_cardapio_cei.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD_CEI}/{alteracao_cardapio_cei.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    assert str(json['uuid']) == str(alteracao_cardapio_cei.uuid)


def test_url_endpoint_alt_card_inicio_error(client_autenticado_vinculo_escola_cardapio, alteracao_cardapio_dre_validar):
    assert str(alteracao_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_dre_validar.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Erro de transição de estado: Transition 'inicia_fluxo'"
                                         " isn't available from state 'DRE_A_VALIDAR'."}


def test_url_endpoint_alt_card_dre_valida(client_autenticado_vinculo_dre_cardapio, alteracao_cardapio_dre_validar):
    assert str(alteracao_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_dre_validar.uuid}/{constants.DRE_VALIDA_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    assert str(json['uuid']) == str(alteracao_cardapio_dre_validar.uuid)


def test_url_endpoint_alt_card_codae_questiona(client_autenticado_vinculo_codae_cardapio,
                                               alteracao_cardapio_dre_validado):
    assert str(alteracao_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    observacao_questionamento_codae = 'VAI_DAR?'
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_dre_validado.uuid}/{constants.CODAE_QUESTIONA_PEDIDO}/',
        data={'observacao_questionamento_codae': observacao_questionamento_codae},
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['logs'][0]['justificativa'] == observacao_questionamento_codae
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO
    assert str(json['uuid']) == str(alteracao_cardapio_dre_validado.uuid)
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_dre_validado.uuid}/{constants.CODAE_QUESTIONA_PEDIDO}/',
        data={'observacao_questionamento_codae': observacao_questionamento_codae},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Erro de transição de estado: Transition 'codae_questiona'"
                                         " isn't available from state 'CODAE_QUESTIONADO'."}


def test_url_endpoint_alt_card_terceirizada_responde_questionamento(client_autenticado_vinculo_terceirizada_cardapio,
                                                                    alteracao_cardapio_codae_questionado):
    assert str(alteracao_cardapio_codae_questionado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO
    justificativa = 'VAI DAR NÃO :('
    resposta_sim_nao = False
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/'
        f'{alteracao_cardapio_codae_questionado.uuid}/'
        f'{constants.TERCEIRIZADA_RESPONDE_QUESTIONAMENTO}/',
        data={'justificativa': justificativa, 'resposta_sim_nao': resposta_sim_nao},
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['logs'][0]['justificativa'] == justificativa
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO
    assert str(json['uuid']) == str(alteracao_cardapio_codae_questionado.uuid)
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/'
        f'{alteracao_cardapio_codae_questionado.uuid}/'
        f'{constants.TERCEIRIZADA_RESPONDE_QUESTIONAMENTO}/',
        data={'justificativa': justificativa, 'resposta_sim_nao': resposta_sim_nao},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Erro de transição de estado: Transition '
                                         "'terceirizada_responde_questionamento' isn't available from state "
                                         "'TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO'."}


@freeze_time('2019-10-1')
def test_url_endpoint_alt_card_escola_cancela(client_autenticado_vinculo_escola_cardapio,
                                              alteracao_cardapio_codae_questionado):
    assert str(alteracao_cardapio_codae_questionado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_codae_questionado.uuid}/{constants.ESCOLA_CANCELA}/',
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU
    assert str(json['uuid']) == str(alteracao_cardapio_codae_questionado.uuid)
    response = client_autenticado_vinculo_escola_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_codae_questionado.uuid}/{constants.ESCOLA_CANCELA}/',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Erro de transição de estado: Já está cancelada'}


def test_url_endpoint_alt_card_dre_valida_error(client_autenticado_vinculo_dre_cardapio, alteracao_cardapio):
    assert str(alteracao_cardapio.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/{constants.DRE_VALIDA_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Erro de transição de estado: Transition 'dre_valida'"
                                         " isn't available from state 'RASCUNHO'."}


def test_url_endpoint_alt_card_dre_nao_valida(client_autenticado_vinculo_dre_cardapio, alteracao_cardapio_dre_validar):
    assert str(alteracao_cardapio_dre_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_dre_validar.uuid}/{constants.DRE_NAO_VALIDA_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.DRE_NAO_VALIDOU_PEDIDO_ESCOLA
    assert str(json['uuid']) == str(alteracao_cardapio_dre_validar.uuid)


def test_url_endpoint_alt_card_dre_nao_valida_error(client_autenticado_vinculo_dre_cardapio,
                                                    alteracao_cardapio_dre_validado):
    assert str(alteracao_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_dre_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_dre_validado.uuid}/{constants.DRE_NAO_VALIDA_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Erro de transição de estado: Transition 'dre_nao_valida' "
                                         "isn't available from state 'DRE_VALIDADO'."}


def test_url_endpoint_alt_card_codae_autoriza(client_autenticado_vinculo_codae_cardapio,
                                              alteracao_cardapio_dre_validado):
    assert str(alteracao_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_dre_validado.uuid}/{constants.CODAE_AUTORIZA_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    assert str(json['uuid']) == str(alteracao_cardapio_dre_validado.uuid)


def test_url_endpoint_alt_card_codae_autoriza_error(client_autenticado_vinculo_codae_cardapio, alteracao_cardapio):
    assert str(alteracao_cardapio.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/{constants.CODAE_AUTORIZA_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Erro de transição de estado: Transition 'codae_autoriza_questionamento' "
                                         "isn't available from state 'RASCUNHO'."}


def test_url_endpoint_alt_card_codae_nega(client_autenticado_vinculo_codae_cardapio, alteracao_cardapio_dre_validado):
    assert str(alteracao_cardapio_dre_validado.status) == PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_dre_validado.uuid}/{constants.CODAE_NEGA_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO
    assert str(json['uuid']) == str(alteracao_cardapio_dre_validado.uuid)


def test_url_endpoint_alt_card_codae_nega_error(client_autenticado_vinculo_codae_cardapio,
                                                alteracao_cardapio_codae_autorizado):
    assert str(alteracao_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado_vinculo_codae_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_codae_autorizado.uuid}/{constants.CODAE_NEGA_PEDIDO}/'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Erro de transição de estado: Transition 'codae_nega_questionamento'"
                                         " isn't available from state 'CODAE_AUTORIZADO'."}


def test_url_endpoint_alt_card_terceirizada_ciencia(client_autenticado_vinculo_terceirizada_cardapio,
                                                    alteracao_cardapio_codae_autorizado):
    assert str(alteracao_cardapio_codae_autorizado.status) == PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio_codae_autorizado.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
    assert str(json['uuid']) == str(alteracao_cardapio_codae_autorizado.uuid)


def test_url_endpoint_alt_card_terceirizada_ciencia_error(client_autenticado_vinculo_terceirizada_cardapio,
                                                          alteracao_cardapio):
    assert str(alteracao_cardapio.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado_vinculo_terceirizada_cardapio.patch(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/{constants.TERCEIRIZADA_TOMOU_CIENCIA}/'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'terceirizada_toma_ciencia'"
                  " isn't available from state 'RASCUNHO'."}


def test_url_endpoint_alt_card_relatorio(client_autenticado, alteracao_cardapio):
    response = client_autenticado.get(
        f'/{ENDPOINT_ALTERACAO_CARD}/{alteracao_cardapio.uuid}/{constants.RELATORIO}/'
    )
    id_externo = alteracao_cardapio.id_externo
    assert response.status_code == status.HTTP_200_OK
    assert response._headers['content-type'] == ('Content-Type', 'application/pdf')
    assert response._headers['content-disposition'] == (
        'Content-Disposition', f'filename="alteracao_cardapio_{id_externo}.pdf"')
    assert 'PDF-1.5' in str(response.content)
    assert isinstance(response.content, bytes)


def test_url_endpoint_alt_card_cei_relatorio(client_autenticado, alteracao_cardapio_cei):
    response = client_autenticado.get(
        f'/{ENDPOINT_ALTERACAO_CARD_CEI}/{alteracao_cardapio_cei.uuid}/{constants.RELATORIO}/'
    )
    id_externo = alteracao_cardapio_cei.id_externo
    assert response.status_code == status.HTTP_200_OK
    assert response._headers['content-type'] == ('Content-Type', 'application/pdf')
    assert response._headers['content-disposition'] == (
        'Content-Disposition', f'filename="alteracao_cardapio_{id_externo}.pdf"')
    assert 'PDF-1.5' in str(response.content)
    assert isinstance(response.content, bytes)


def test_url_endpoint_get_vinculos_tipo_alimentacao(client_autenticado_vinculo_escola, vinculo_tipo_alimentacao):
    response = client_autenticado_vinculo_escola.get(
        f'/{ENDPOINT_VINCULOS_ALIMENTACAO}/'
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()['results']
    assert json[0]['uuid'] == str(vinculo_tipo_alimentacao.uuid)
    assert json[0]['periodo_escolar']['uuid'] == str(vinculo_tipo_alimentacao.periodo_escolar.uuid)
    assert json[0]['tipo_unidade_escolar']['uuid'] == str(vinculo_tipo_alimentacao.tipo_unidade_escolar.uuid)
    assert len(json[0]['tipos_alimentacao']) == 5

    # testa endpoint de filtro tipo_ue
    response = client_autenticado_vinculo_escola.get(
        f'/{ENDPOINT_VINCULOS_ALIMENTACAO}/tipo_unidade_escolar/{vinculo_tipo_alimentacao.tipo_unidade_escolar.uuid}/',
    )
    json = response.json()['results']
    assert json[0]['uuid'] == str(vinculo_tipo_alimentacao.uuid)
    assert json[0]['periodo_escolar']['uuid'] == str(vinculo_tipo_alimentacao.periodo_escolar.uuid)
    assert json[0]['tipo_unidade_escolar']['uuid'] == str(vinculo_tipo_alimentacao.tipo_unidade_escolar.uuid)
    assert len(json[0]['tipos_alimentacao']) == 5


def test_endpoint_horario_do_combo_tipo_alimentacao_unidade_escolar(client_autenticado_vinculo_escola,
                                                                    horario_combo_tipo_alimentacao):
    response = client_autenticado_vinculo_escola.get(
        f'/{ENDPOINT_HORARIO_DO_COMBO}/escola/{horario_combo_tipo_alimentacao.escola.uuid}/'
    )
    json = response.json()['results']
    assert response.status_code == status.HTTP_200_OK
    assert json[0]['uuid'] == str(horario_combo_tipo_alimentacao.uuid)
    assert json[0]['hora_inicial'] == horario_combo_tipo_alimentacao.hora_inicial
    assert json[0]['hora_final'] == horario_combo_tipo_alimentacao.hora_final
    assert json[0]['combo_tipos_alimentacao'] == {
        'uuid': '9fe31f4a-716b-4677-9d7d-2868557cf954',
        'tipos_alimentacao': [
            {'uuid': 'c42a24bb-14f8-4871-9ee8-05bc42cf3061', 'nome': 'Lanche'},
            {'uuid': '22596464-271e-448d-bcb3-adaba43fffc8', 'nome': 'Refeição'}
        ],
        'vinculo': '3bdf8144-9b17-495a-8387-5ce0d2a6120a',
        'substituicoes': [],
        'label': 'Lanche e Refeição'
    }
    assert json[0]['escola'] == {
        'uuid': 'a627fc63-16fd-482c-a877-16ebc1a82e57',
        'nome': 'EMEF JOAO MENDES',
        'codigo_eol': '000546',
        'quantidade_alunos': 0
    }


def checa_se_terceirizada_marcou_conferencia_na_gestao_de_alimentacao(client_autenticado,
                                                                      classe,
                                                                      path):
    obj = classe.objects.first()
    assert not obj.terceirizada_conferiu_gestao

    response = client_autenticado.patch(
        f'/{path}/{obj.uuid}/marcar-conferida/',
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert 'terceirizada_conferiu_gestao' in result.keys()
    assert result['terceirizada_conferiu_gestao']

    obj = classe.objects.first()
    assert obj.terceirizada_conferiu_gestao


def test_terceirizada_marca_conferencia_inversao_cardapio_viewset(client_autenticado,
                                                                  inversao_dia_cardapio):
    checa_se_terceirizada_marcou_conferencia_na_gestao_de_alimentacao(
        client_autenticado,
        InversaoCardapio,
        'inversoes-dia-cardapio')


def test_terceirizada_marca_conferencia_grupo_suspensao_alimentacao_viewset(client_autenticado,
                                                                            grupo_suspensao_alimentacao):
    checa_se_terceirizada_marcou_conferencia_na_gestao_de_alimentacao(
        client_autenticado,
        GrupoSuspensaoAlimentacao,
        'grupos-suspensoes-alimentacao')


def test_terceirizada_marca_conferencia_alteracao_cardapio_viewset(client_autenticado,
                                                                   alteracao_cardapio):
    checa_se_terceirizada_marcou_conferencia_na_gestao_de_alimentacao(
        client_autenticado,
        AlteracaoCardapio,
        'alteracoes-cardapio')
