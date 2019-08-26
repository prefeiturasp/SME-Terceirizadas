from rest_framework import status


# TODO Encontrar forma de testar com autenticação no JWT
def test_url_endpoint_painel_dre(client):
    response = client.get('/dre-pendentes-aprovacao/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def base_codae(client, resource):
    endpoint = f'/codae-solicitacoes/{resource}/'
    response = client.get(endpoint)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_url_endpoint_painel_codae_pendentes_aprovacao(client):
    base_codae(client, 'pendentes-aprovacao')


def test_url_endpoint_painel_codae_aprovados(client):
    base_codae(client, 'aprovados')


def test_url_endpoint_painel_codae_cancelados(client):
    base_codae(client, 'cancelados')


def test_url_endpoint_painel_codae_solicitacoes_revisao(client):
    base_codae(client, 'solicitacoes-revisao')
