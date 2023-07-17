import pytest
from rest_framework import status

from ...utils import UnidadeMedidaPagination

pytestmark = pytest.mark.django_db


def test_url_unidades_medida_list(client_autenticado, unidades_medida_logistica):
    """Deve retornar lista paginada de unidades de medida."""
    response = client_autenticado.get('/unidades-medida-logistica/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == len(unidades_medida_logistica)
    assert len(response.data['results']) == UnidadeMedidaPagination.page_size
    assert response.data['next'] is not None
