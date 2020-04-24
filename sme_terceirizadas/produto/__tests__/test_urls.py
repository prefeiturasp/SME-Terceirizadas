import pytest
from rest_framework import status

from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import HomologacaoProdutoWorkflow

pytestmark = pytest.mark.django_db


def test_url_endpoint_inclusao_normal_codae_homologa(client_autenticado_vinculo_codae_produto,
                                                     homologacao_produto_pendente_homologacao):
    assert homologacao_produto_pendente_homologacao.status == HomologacaoProdutoWorkflow.CODAE_PENDENTE_HOMOLOGACAO
    response = client_autenticado_vinculo_codae_produto.patch(
        f'/homologacoes-produtos/{homologacao_produto_pendente_homologacao.uuid}/{constants.CODAE_HOMOLOGA}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == HomologacaoProdutoWorkflow.CODAE_HOMOLOGADO
    response = client_autenticado_vinculo_codae_produto.patch(
        f'/homologacoes-produtos/{homologacao_produto_pendente_homologacao.uuid}/{constants.CODAE_HOMOLOGA}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'codae_homologa' isn't available from state "
                  "'CODAE_HOMOLOGADO'."}


def test_url_endpoint_inclusao_normal_codae_nao_homologa(client_autenticado_vinculo_codae_produto,
                                                         homologacao_produto_pendente_homologacao):
    assert homologacao_produto_pendente_homologacao.status == HomologacaoProdutoWorkflow.CODAE_PENDENTE_HOMOLOGACAO
    response = client_autenticado_vinculo_codae_produto.patch(
        f'/homologacoes-produtos/{homologacao_produto_pendente_homologacao.uuid}/{constants.CODAE_NAO_HOMOLOGA}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == HomologacaoProdutoWorkflow.CODAE_NAO_HOMOLOGADO
    response = client_autenticado_vinculo_codae_produto.patch(
        f'/homologacoes-produtos/{homologacao_produto_pendente_homologacao.uuid}/{constants.CODAE_NAO_HOMOLOGA}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'codae_nao_homologa' isn't available from state "
                  "'CODAE_NAO_HOMOLOGADO'."}


def test_url_endpoint_inclusao_normal_codae_pede_analise_sensorial(client_autenticado_vinculo_codae_produto,
                                                                   homologacao_produto_pendente_homologacao):
    assert homologacao_produto_pendente_homologacao.status == HomologacaoProdutoWorkflow.CODAE_PENDENTE_HOMOLOGACAO
    response = client_autenticado_vinculo_codae_produto.patch(
        f'/homologacoes-produtos/{homologacao_produto_pendente_homologacao.uuid}/'
        f'{constants.CODAE_PEDE_ANALISE_SENSORIAL}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_SENSORIAL
    response = client_autenticado_vinculo_codae_produto.patch(
        f'/homologacoes-produtos/{homologacao_produto_pendente_homologacao.uuid}/'
        f'{constants.CODAE_PEDE_ANALISE_SENSORIAL}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'codae_pede_analise_sensorial' isn't available from state "
                  "'CODAE_PEDIU_ANALISE_SENSORIAL'."}
