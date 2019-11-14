import pytest
from rest_framework import status

from ..models import SolicitacaoKitLancheAvulsa
from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow

pytestmark = pytest.mark.django_db


def base_get_request(client_autenticado, resource):
    endpoint = f'/{resource}/'
    response = client_autenticado.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_kit_lanches(client_autenticado):
    base_get_request(client_autenticado, 'kit-lanches')


def test_url_endpoint_solicitacoes_kit_lanche_avulsa(client_autenticado, solicitacao_avulsa):
    # TODO: testar o POST também
    response = client_autenticado.get('/solicitacoes-kit-lanche-avulsa/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['count'] == 1
    kit_lanche_avulso = json['results'][0]
    kit_base = kit_lanche_avulso['solicitacao_kit_lanche']
    assert len(kit_base['kits']) == 3
    for key in ['descricao', 'motivo', 'criado_em', 'data', 'tempo_passeio_explicacao', 'kits', 'tempo_passeio',
                'uuid']:
        assert key in kit_base.keys()
    assert 'escola' in kit_lanche_avulso.keys()
    for key in ['prioridade', 'id_externo', 'logs', 'quantidade_alimentacoes', 'data', 'uuid', 'status', 'local',
                'quantidade_alunos', 'criado_por', 'rastro_escola', 'rastro_dre', 'rastro_lote', 'rastro_terceirizada']:
        assert key in kit_lanche_avulso


def test_url_endpoint_solicitacoes_kit_lanche_avulsa_inicio_fluxo(client_autenticado, solicitacao_avulsa):
    assert str(solicitacao_avulsa.status) == PedidoAPartirDaEscolaWorkflow.RASCUNHO
    response = client_autenticado.patch(
        f'/solicitacoes-kit-lanche-avulsa/{solicitacao_avulsa.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )

    json = response.json()
    assert json['status'] == 'DRE_A_VALIDAR'
    solicitacao_avulsa_atualizada = SolicitacaoKitLancheAvulsa.objects.get(id=solicitacao_avulsa.id)
    assert str(solicitacao_avulsa_atualizada.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR
    assert str(json['uuid']) == str(solicitacao_avulsa.uuid)


def test_url_endpoint_solicitacoes_kit_lanche_avulsa_inicio_fluxo_exception(client_autenticado,
                                                                            solicitacao_avulsa_dre_a_validar):
    assert str(solicitacao_avulsa_dre_a_validar.status) == PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR

    response = client_autenticado.patch(
        f'/solicitacoes-kit-lanche-avulsa/{solicitacao_avulsa_dre_a_validar.uuid}/{constants.ESCOLA_INICIO_PEDIDO}/'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'inicia_fluxo' isn't available from state 'DRE_A_VALIDAR'."}


def test_url_endpoint_solicitacoes_kit_lanche_unificada(client_autenticado):
    base_get_request(client_autenticado, 'solicitacoes-kit-lanche-unificada')
