from rest_framework import status

ENDPOINT_ALUNOS_POR_PERIODO = 'quantidade-alunos-por-periodo'
ENDPOINT_LOTES = 'lotes'


def test_url_endpoint_quantidade_alunos_por_periodo(client_autenticado, escola):
    response = client_autenticado.get(
        f'/{ENDPOINT_ALUNOS_POR_PERIODO}/escola/{escola.uuid}/'
    )
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_lotes(client_autenticado):
    response = client_autenticado.get(
        f'/{ENDPOINT_LOTES}/'
    )
    assert response.status_code == status.HTTP_200_OK


def test_url_endpoint_lotes_delete(client_autenticado, lote):
    response = client_autenticado.delete(
        f'/{ENDPOINT_LOTES}/{lote.uuid}/'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
