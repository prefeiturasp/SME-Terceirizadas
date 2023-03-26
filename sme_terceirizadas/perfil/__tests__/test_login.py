import pytest
from rest_framework import status
from utility.carga_dados.perfil.importa_dados import ProcessaPlanilhaUsuarioServidorCoreSSO

from sme_terceirizadas.dados_comuns.constants import ADMINISTRADOR_UE, DIRETOR_UE
from sme_terceirizadas.eol_servico.utils import EOLServicoSGP
from sme_terceirizadas.escola.__tests__.conftest import mocked_response
from sme_terceirizadas.escola.services import NovoSGPServicoLogado
from sme_terceirizadas.perfil.__tests__.conftest import (
    mocked_response_autentica_coresso_diretor,
    mocked_response_autentica_coresso_diretor_login_errado,
    mocked_response_get_dados_usuario_coresso,
    mocked_response_get_dados_usuario_coresso_adm_escola,
    mocked_response_get_dados_usuario_coresso_sem_acesso_automatico
)
from sme_terceirizadas.perfil.models import Usuario
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


def test_login_coresso_erro_usuario_nao_existe(client_autenticado_da_escola, monkeypatch):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'login': '1234568',
        'senha': 'admin@123'
    }

    monkeypatch.setattr(AutenticacaoService, 'autentica',
                        lambda p1, p2: mocked_response(mocked_response_autentica_coresso_diretor_login_errado(), 200))
    monkeypatch.setattr(EOLServicoSGP, 'get_dados_usuario',
                        lambda p1: mocked_response(mocked_response_get_dados_usuario_coresso(), 200))
    response = client_autenticado_da_escola.post('/login/', headers=headers, data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Usuário não encontrado.'}


def test_login_coresso_diretor_era_adm_escola(client_autenticado_da_escola_adm, monkeypatch):
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
    response = client_autenticado_da_escola_adm.post('/login/', headers=headers, data=data)
    assert response.status_code == status.HTTP_200_OK
    usuario = Usuario.objects.get(username=data['login'])
    assert usuario.vinculo_atual.perfil.nome == DIRETOR_UE


def test_login_coresso_diretor_sem_acesso_ao_coresso(client_autenticado_da_escola, monkeypatch):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'login': '1234567',
        'senha': 'admin@123'
    }

    monkeypatch.setattr(AutenticacaoService, 'autentica',
                        lambda p1, p2: mocked_response({}, 200))
    monkeypatch.setattr(EOLServicoSGP, 'get_dados_usuario',
                        lambda p1: mocked_response(mocked_response_get_dados_usuario_coresso(), 200))
    monkeypatch.setattr(NovoSGPServicoLogado, 'pegar_token_acesso',
                        lambda p1, p2, p3: mocked_response({'token': '#ABC123'}, 200))
    monkeypatch.setattr(ProcessaPlanilhaUsuarioServidorCoreSSO, 'cria_usuario_servidor',
                        lambda p1, p2, p3: None)
    response = client_autenticado_da_escola.post('/login/', headers=headers, data=data)
    assert response.status_code == status.HTTP_200_OK
    usuario = Usuario.objects.get(username=data['login'])
    assert usuario.vinculo_atual.perfil.nome == DIRETOR_UE


def test_login_usuario_com_acesso_automatico_adm_escola(client_autenticado_da_escola_adm, monkeypatch):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'login': '1234567',
        'senha': 'admin@123'
    }

    monkeypatch.setattr(AutenticacaoService, 'autentica',
                        lambda p1, p2: mocked_response({}, 200))
    monkeypatch.setattr(EOLServicoSGP, 'get_dados_usuario',
                        lambda p1: mocked_response(
                            mocked_response_get_dados_usuario_coresso_adm_escola(), 200))
    monkeypatch.setattr(NovoSGPServicoLogado, 'pegar_token_acesso',
                        lambda p1, p2, p3: mocked_response({'token': '#ABC123'}, 200))
    monkeypatch.setattr(ProcessaPlanilhaUsuarioServidorCoreSSO, 'cria_usuario_servidor',
                        lambda p1, p2, p3: None)
    response = client_autenticado_da_escola_adm.post('/login/', headers=headers, data=data)
    assert response.status_code == status.HTTP_200_OK
    usuario = Usuario.objects.get(username=data['login'])
    assert usuario.vinculo_atual.perfil.nome == ADMINISTRADOR_UE


def test_login_coresso_diretor_sem_vinculo_no_sigpae(client_autenticado_da_escola_sem_vinculo, monkeypatch):
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
    response = client_autenticado_da_escola_sem_vinculo.post('/login/', headers=headers, data=data)
    assert response.status_code == status.HTTP_200_OK
    usuario = Usuario.objects.get(username=data['login'])
    assert usuario.vinculo_atual.perfil.nome == DIRETOR_UE


def test_login_coresso_adm_escola_sem_vinculo_no_sigpae(client_autenticado_da_escola_sem_vinculo, monkeypatch):
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
                        lambda p1: mocked_response(mocked_response_get_dados_usuario_coresso_adm_escola(), 200))
    response = client_autenticado_da_escola_sem_vinculo.post('/login/', headers=headers, data=data)
    assert response.status_code == status.HTTP_200_OK
    usuario = Usuario.objects.get(username=data['login'])
    assert usuario.vinculo_atual.perfil.nome == ADMINISTRADOR_UE


def test_login_coresso_cargo_sem_acesso_automatico_sem_vinculo_no_sigpae(client_autenticado_da_escola_sem_vinculo,
                                                                         monkeypatch):
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
                        lambda p1: mocked_response(mocked_response_get_dados_usuario_coresso_sem_acesso_automatico(),
                                                   200))
    response = client_autenticado_da_escola_sem_vinculo.post('/login/', headers=headers, data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Usuário não possui permissão de acesso ao SIGPAE'}
