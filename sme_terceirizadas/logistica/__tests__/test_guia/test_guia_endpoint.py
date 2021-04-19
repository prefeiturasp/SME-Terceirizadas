import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(client_autenticado_dilog, guia):
    response = client_autenticado_dilog.get('/guias-da-requisicao/inconsistencias/')
    assert response.status_code == status.HTTP_200_OK
