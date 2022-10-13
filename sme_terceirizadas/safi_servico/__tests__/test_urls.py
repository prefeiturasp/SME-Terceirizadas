
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_lista_termos_de_contratos(client_autenticado,):
    response = client_autenticado.get(
        f'/dados-contrato-safi/lista-termos-de-contratos/'
    )
    assert response.status_code == status.HTTP_200_OK
