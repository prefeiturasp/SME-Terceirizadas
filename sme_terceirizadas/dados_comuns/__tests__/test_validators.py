import pytest
from freezegun import freeze_time
from rest_framework.exceptions import ValidationError


from ..validators import (deve_pedir_com_antecedencia, campo_deve_ser_deste_tipo, dia_util,
                          nao_pode_ser_feriado, nao_pode_ser_no_passado, campo_nao_pode_ser_nulo,
                          objeto_nao_deve_ter_duplicidade, verificar_se_existe)


@freeze_time('2019-05-22')  # qua
def test_deve_pedir_com_antecedencia(dias_teste_antecedencia):
    dia, dias_antec, esperado = dias_teste_antecedencia
    assert deve_pedir_com_antecedencia(dia, dias_antec) is esperado


@freeze_time('2019-05-22')  # qua
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


@freeze_time('2019-05-22')
def test_nao_pode_ser_passado(dias_futuros):
    dia, esperado = dias_futuros
    assert nao_pode_ser_no_passado(dia) is esperado


@freeze_time('2019-05-22')
def test_nao_pode_ser_passado_raise_exception(dias_passados):
    dia, esperado = dias_passados
    with pytest.raises(ValidationError, match=esperado):
        nao_pode_ser_no_passado(dia)


def test_verificar_se_existe_return_false(validators_models_object):
    obj_model = validators_models_object.__class__
    assert verificar_se_existe(obj_model, numero=11) is False


def test_verificar_se_existe_return_true(validators_models_object):
    obj_model = validators_models_object.__class__
    assert verificar_se_existe(obj_model, numero=10) is True


def test_verificar_se_existe_raise_exception(validators_models_object):
    with pytest.raises(TypeError, match='obj_model deve ser um "django models class"'):
        verificar_se_existe(validators_models_object)


def test_objeto_nao_deve_ter_duplicidade_return_none(validators_models_object):
    obj_model = validators_models_object.__class__
    assert objeto_nao_deve_ter_duplicidade(obj_model, numero=11) is None


def test_objeto_nao_deve_ter_duplicidade_raise_error(validators_models_object):
    obj_model = validators_models_object.__class__
    with pytest.raises(ValidationError, match='Objeto já existe'):
        objeto_nao_deve_ter_duplicidade(obj_model, numero=10)


def test_nao_pode_ser_nulo_valor_none(validators_valor_str):
    with pytest.raises(ValidationError, match='Não pode ser nulo'):
        campo_nao_pode_ser_nulo(validators_valor_str['none'])


def test_nao_pode_ser_nulo_valor_valido(validators_valor_str):
    assert campo_nao_pode_ser_nulo(validators_valor_str['texto']) is None


def test_deve_ser_deste_tipo_valor_rasie_error(validators_valor_str):
    with pytest.raises(ValidationError, match='Deve ser do tipo texto'):
        campo_deve_ser_deste_tipo(validators_valor_str['none'])


def test_deve_ser_deste_tipo_valor_valido(validators_valor_str):
    assert campo_deve_ser_deste_tipo(validators_valor_str['texto']) is None


def test_nao_pode_ser_feriado_raise_error(dias_nao_uteis):
    dia, _ = dias_nao_uteis
    with pytest.raises(ValidationError, match='Não pode ser no feriado'):
        assert nao_pode_ser_feriado(dia)


def test_nao_pode_ser_feriado_valor_valido(dias_uteis):
    dia, _ = dias_uteis
    assert nao_pode_ser_feriado(dia) is None
