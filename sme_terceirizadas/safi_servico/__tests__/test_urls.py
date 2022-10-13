
from unittest.mock import patch

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_contrato(client_autenticado,):
    contrato = '8d21bca3-8f98-4ec4-b823-340eb082e32e'
    api_safi = 'sme_terceirizadas.safi_servico.utils.SAFIService.get_contrato'
    with patch(api_safi):
        response = client_autenticado.get(
            f'/dados-contrato-safi/{contrato}/'
        )
    assert response.status_code == status.HTTP_200_OK


def test_lista_termos_de_contratos(client_autenticado,):
    api_safi = 'sme_terceirizadas.safi_servico.utils.SAFIService.get_termos_de_contratos'
    with patch(api_safi):
        response = client_autenticado.get(
            f'/dados-contrato-safi/lista-termos-de-contratos/'
        )
    assert response.status_code == status.HTTP_200_OK
