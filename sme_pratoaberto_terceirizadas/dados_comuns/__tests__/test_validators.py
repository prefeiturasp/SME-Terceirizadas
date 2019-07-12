import pytest
from freezegun import freeze_time
from rest_framework.exceptions import ValidationError

from ..validators import (deve_pedir_com_antecedencia, dia_util,
                          nao_pode_ser_passado)


@freeze_time("2019-05-22")  # qua
def test_deve_pedir_com_antecedencia(dias_teste_antecedencia):
    dia, dias_antec, esperado = dias_teste_antecedencia
    assert deve_pedir_com_antecedencia(dia, dias_antec) is esperado


@freeze_time("2019-05-22")  # qua
def test_deve_pedir_com_antecedencia_validation_error(dias_teste_antecedencia_erro):
    dia, dias_antec, esperado = dias_teste_antecedencia_erro
    with pytest.raises(ValidationError, match=esperado):
        deve_pedir_com_antecedencia(dia, dias_antec)


def test_dia_util(dias_uteis):
    dia, esperado = dias_uteis
    assert dia_util(dia) is esperado


def test_dia_nao_util(dias_nao_uteis):
    dia, esperado = dias_nao_uteis
    with pytest.raises(ValidationError, match=esperado):
        dia_util(dia)


@freeze_time("2019-05-22")
def test_nao_pode_ser_passado(dias_futuros):
    dia, esperado = dias_futuros
    assert nao_pode_ser_passado(dia) is esperado


@freeze_time("2019-05-22")
def test_nao_pode_ser_passado_raise_exception(dias_passados):
    dia, esperado = dias_passados
    with pytest.raises(ValidationError, match=esperado):
        nao_pode_ser_passado(dia)
