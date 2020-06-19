import json

import pytest
from rest_framework import status

from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import HomologacaoProdutoWorkflow

pytestmark = pytest.mark.django_db

ENDPOINT_ANALISE_SENSORIAL = 'analise-sensorial'
TERCEIRIZADA_RESPONDE = 'terceirizada-responde-analise-sensorial'


def test_url_endpoint_homologacao_produto_codae_homologa(client_autenticado_vinculo_codae_produto,
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
    response = client_autenticado_vinculo_codae_produto.get(
        f'/painel-gerencial-homologacoes-produtos/filtro-por-status/codae_homologado/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('results')) == 1


def test_url_endpoint_homologacao_produto_codae_nao_homologa(client_autenticado_vinculo_codae_produto,
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
    response = client_autenticado_vinculo_codae_produto.get(
        f'/painel-gerencial-homologacoes-produtos/filtro-por-status/codae_nao_homologado/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('results')) == 1


def test_url_endpoint_homologacao_produto_codae_questiona(client_autenticado_vinculo_codae_produto,
                                                          homologacao_produto_pendente_homologacao):
    assert homologacao_produto_pendente_homologacao.status == HomologacaoProdutoWorkflow.CODAE_PENDENTE_HOMOLOGACAO
    response = client_autenticado_vinculo_codae_produto.patch(
        f'/homologacoes-produtos/{homologacao_produto_pendente_homologacao.uuid}/'
        f'{constants.CODAE_QUESTIONA_PEDIDO}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == HomologacaoProdutoWorkflow.CODAE_QUESTIONADO
    response = client_autenticado_vinculo_codae_produto.patch(
        f'/homologacoes-produtos/{homologacao_produto_pendente_homologacao.uuid}/'
        f'{constants.CODAE_QUESTIONA_PEDIDO}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Erro de transição de estado: Transition 'codae_questiona' isn't available from state "
                  "'CODAE_QUESTIONADO'."}
    response = client_autenticado_vinculo_codae_produto.get(
        f'/painel-gerencial-homologacoes-produtos/filtro-por-status/codae_questionado/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('results')) == 1


def test_url_endpoint_homologacao_produto_codae_pede_analise_sensorial(client_autenticado_vinculo_codae_produto,
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
    response = client_autenticado_vinculo_codae_produto.get(
        f'/painel-gerencial-homologacoes-produtos/filtro-por-status/codae_pediu_analise_sensorial/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('results')) == 1


def test_url_endpoint_resposta_analise_sensorial(client_autenticado_vinculo_terceirizada_homologacao):
    body_content = {
        'data': '2020-05-23',
        'homologacao_de_produto': '774ad907-d871-4bfd-b1aa-d4e0ecb6c01f',
        'hora': '20:01:54',
        'registro_funcional': '02564875',
        'responsavel_produto': 'RESPONSAVEL TESTE',
        'observacao': 'OBSERVACAO',
        'anexos': []
    }
    client, homologacao_produto, homologacao_produto_1 = client_autenticado_vinculo_terceirizada_homologacao
    assert homologacao_produto.status == HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_SENSORIAL
    response = client.post(f'/{ENDPOINT_ANALISE_SENSORIAL}/{TERCEIRIZADA_RESPONDE}/', data=json.dumps(body_content),
                           content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'homologacao_de_produto': '774ad907-d871-4bfd-b1aa-d4e0ecb6c01f', 'data': '23/05/2020',
                               'hora': '20:01:54', 'anexos': [], 'responsavel_produto': 'RESPONSAVEL TESTE',
                               'registro_funcional': '02564875', 'observacao': 'OBSERVACAO'}

    assert homologacao_produto_1.status == HomologacaoProdutoWorkflow.CODAE_PENDENTE_HOMOLOGACAO
    body_content['homologacao_de_produto'] = '774ad907-d871-4bfd-b1aa-d4e0ecb6c05a'
    response = client.post(f'/{ENDPOINT_ANALISE_SENSORIAL}/{TERCEIRIZADA_RESPONDE}/', data=json.dumps(body_content),
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
