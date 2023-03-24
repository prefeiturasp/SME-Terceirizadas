import pytest
from rest_framework import status

from sme_terceirizadas.eol_servico.utils import EOLServicoSGP
from sme_terceirizadas.escola.__tests__.conftest import mocked_response
from sme_terceirizadas.perfil.__tests__.conftest import mocked_response_autentica_coresso_diretor, \
    mocked_response_get_dados_usuario_coresso
from sme_terceirizadas.perfil.services.autenticacao_service import AutenticacaoService

pytestmark = pytest.mark.django_db


def test_login_coresso_diretor_sucesso(client_autenticado_da_escola, monkeypatch):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'login': '1234567',
        'senha': 'admin@123'
    }

    monkeypatch.setattr(AutenticacaoService, 'autentica',
                        lambda p1, p2: mocked_response(mocked_response_autentica_coresso_diretor(), 200))
    monkeypatch.setattr(EOLServicoSGP, 'get_dados_usuario',
                        lambda p1: mocked_response(mocked_response_get_dados_usuario_coresso(), 200))
    response = client_autenticado_da_escola.post('/login/', headers=headers, data=data)
    assert response.status_code == status.HTTP_200_OK
