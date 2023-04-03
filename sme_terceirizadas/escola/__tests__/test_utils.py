import pytest

from ...eol_servico.utils import EOLException, EOLServicoSGP
from ..utils import meses_para_mes_e_ano_string
from .conftest import mocked_response


def test_meses_para_mes_e_ano_string():
    assert meses_para_mes_e_ano_string(0) == '0 meses'
    assert meses_para_mes_e_ano_string(1) == '1 mês'
    assert meses_para_mes_e_ano_string(2) == '2 meses'
    assert meses_para_mes_e_ano_string(3) == '3 meses'
    assert meses_para_mes_e_ano_string(11) == '11 meses'
    assert meses_para_mes_e_ano_string(12) == '1 ano'
    assert meses_para_mes_e_ano_string(13) == '1 ano e 1 mês'
    assert meses_para_mes_e_ano_string(14) == '1 ano e 2 meses'
    assert meses_para_mes_e_ano_string(15) == '1 ano e 3 meses'
    assert meses_para_mes_e_ano_string(23) == '1 ano e 11 meses'
    assert meses_para_mes_e_ano_string(24) == '2 anos'
    assert meses_para_mes_e_ano_string(25) == '2 anos e 1 mês'
    assert meses_para_mes_e_ano_string(26) == '2 anos e 2 meses'
    assert meses_para_mes_e_ano_string(27) == '2 anos e 3 meses'
    assert meses_para_mes_e_ano_string(35) == '2 anos e 11 meses'
    assert meses_para_mes_e_ano_string(36) == '3 anos'


def test_redefine_senha_coresso(client_autenticado_da_escola, monkeypatch):
    monkeypatch.setattr(EOLServicoSGP, 'chamada_externa_altera_senha',
                        lambda p1: mocked_response({}, 200))
    response = EOLServicoSGP.redefine_senha('123456', 'adminadmin')
    assert response == 'OK'


def test_redefine_senha_coresso_eol_exception(client_autenticado_da_escola, monkeypatch):
    monkeypatch.setattr(EOLServicoSGP, 'chamada_externa_altera_senha',
                        lambda p1: mocked_response({'erro': 'EOL fora do ar'}, 400))
    with pytest.raises(EOLException):
        EOLServicoSGP.redefine_senha('123456', 'adminadmin')


def test_redefine_email_coresso(client_autenticado_da_escola, monkeypatch):
    monkeypatch.setattr(EOLServicoSGP, 'chamada_externa_altera_email_coresso',
                        lambda p1: mocked_response({}, 200))
    response = EOLServicoSGP.redefine_email('123456', 'adminadmin')
    assert response == 'OK'


def test_redefine_email_coresso_eol_exception(client_autenticado_da_escola, monkeypatch):
    monkeypatch.setattr(EOLServicoSGP, 'chamada_externa_altera_email_coresso',
                        lambda p1: mocked_response({'erro': 'EOL fora do ar'}, 400))
    with pytest.raises(EOLException):
        EOLServicoSGP.redefine_email('123456', 'adminadmin')


def test_criar_usuario_coresso(client_autenticado_da_escola, monkeypatch):
    monkeypatch.setattr(EOLServicoSGP, 'chamada_externa_criar_usuario_coresso',
                        lambda p1, p2: mocked_response({}, 200))
    response = EOLServicoSGP.cria_usuario_core_sso('123456', 'FULANO DA SILVA', 'fulano@silva.com')
    assert response == 'OK'


def test_criar_usuario_coresso_eol_exception(client_autenticado_da_escola, monkeypatch):
    monkeypatch.setattr(EOLServicoSGP, 'chamada_externa_criar_usuario_coresso',
                        lambda p1, p2: mocked_response({'erro': 'EOL fora do ar'}, 400))
    with pytest.raises(EOLException):
        EOLServicoSGP.cria_usuario_core_sso('123456', 'FULANO DA SILVA', 'fulano@silva.com')
