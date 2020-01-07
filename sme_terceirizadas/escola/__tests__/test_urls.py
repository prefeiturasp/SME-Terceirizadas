from rest_framework import status

ENDPOINT_ALUNOS_POR_PERIODO = 'quantidade-alunos-por-periodo'


def test_url_endpoint_quantidade_alunos_por_periodo(client_autenticado, escola):
    response = client_autenticado.get(
        f'/{ENDPOINT_ALUNOS_POR_PERIODO}/escola/{escola.uuid}/'
    )
    assert response.status_code == status.HTTP_200_OK
