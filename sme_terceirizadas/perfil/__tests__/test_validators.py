import pytest
from rest_framework.exceptions import ValidationError

from ..api.validators import registro_funcional_e_cpf_sao_da_mesma_pessoa, senha_deve_ser_igual_confirmar_senha

pytestmark = pytest.mark.django_db


def test_senha_deve_ser_igual_confirmar_senha():
    assert senha_deve_ser_igual_confirmar_senha('1', '1') is True
    assert senha_deve_ser_igual_confirmar_senha('134', '134') is True
    assert senha_deve_ser_igual_confirmar_senha('!@#$%', '!@#$%') is True
    with pytest.raises(ValidationError, match='Senha e confirmar senha divergem'):
        senha_deve_ser_igual_confirmar_senha('134', '1343')
        senha_deve_ser_igual_confirmar_senha('senha', 'senha1')


def test_registro_funcional_e_cpf_sao_da_mesma_pessoa(usuario):
    assert registro_funcional_e_cpf_sao_da_mesma_pessoa(
        usuario,
        registro_funcional='1234567',
        cpf='52347255100'
    ) is True
    with pytest.raises(ValidationError, match='Erro ao cadastrar usuário'):
        registro_funcional_e_cpf_sao_da_mesma_pessoa(
            usuario,
            registro_funcional='1234567',
            cpf='52347255101'
        )
        registro_funcional_e_cpf_sao_da_mesma_pessoa(
            usuario,
            registro_funcional='1234568',
            cpf='52347255100'
        )
