import pytest
from rest_framework.exceptions import ValidationError

from ..api.validators import senha_deve_ser_igual_confirmar_senha


def test_senha_deve_ser_igual_confirmar_senha():
    assert senha_deve_ser_igual_confirmar_senha('1', '1') is True
    assert senha_deve_ser_igual_confirmar_senha('134', '134') is True
    assert senha_deve_ser_igual_confirmar_senha('!@#$%', '!@#$%') is True
    with pytest.raises(ValidationError, match='Senha e confirmar senha divergem'):
        senha_deve_ser_igual_confirmar_senha('134', '1343')
        senha_deve_ser_igual_confirmar_senha('senha', 'senha1')
