import datetime

import pytest
from freezegun import freeze_time
from rest_framework.exceptions import ValidationError

from sme_pratoaberto_terceirizadas.dados_comuns.validators import deve_pedir_com_antecedencia, dia_util, nao_pode_ser_passado


@freeze_time("2019-05-22")  # qua
def test_deve_pedir_com_antecedencia():
    t1 = datetime.date(2019, 5, 27)  # seg
    t2 = datetime.date(2019, 5, 28)  # ter
    t3 = datetime.date(2019, 5, 29)  # qua
    t4 = datetime.date(2019, 5, 30)  # qui
    assert deve_pedir_com_antecedencia(t1, 2) is True
    assert deve_pedir_com_antecedencia(t2, 2) is True
    assert deve_pedir_com_antecedencia(t3, 2) is True
    assert deve_pedir_com_antecedencia(t4, 2) is True


@freeze_time("2019-06-10")  # seg
def test_deve_pedir_com_antecedencia_t2():
    t3 = datetime.date(2019, 6, 13)  # qua
    t4 = datetime.date(2019, 6, 14)  # qui
    t5 = datetime.date(2019, 6, 17)  # seg
    t6 = datetime.date(2019, 6, 18)  # ter

    assert deve_pedir_com_antecedencia(t3, 2) is True
    assert deve_pedir_com_antecedencia(t4, 2) is True
    assert deve_pedir_com_antecedencia(t5, 2) is True
    assert deve_pedir_com_antecedencia(t6, 2) is True


@freeze_time("2019-05-22")  # qua
def test_deve_pedir_com_antecedencia_validation_error():
    t1 = datetime.date(2019, 5, 27)  # seg passaram 3 dias uteis
    t2 = datetime.date(2019, 5, 28)  # ter passaram 4 dias uteis
    t3 = datetime.date(2019, 5, 23)  # qui passaram 1 dias uteis
    t4 = datetime.date(2019, 5, 21)  # ter um dia antes
    with pytest.raises(ValidationError, match='Deve pedir com pelo menos 5 dias úteis de antecedência'):
        deve_pedir_com_antecedencia(t1, 5)
    with pytest.raises(ValidationError, match='Deve pedir com pelo menos 5 dias úteis de antecedência'):
        deve_pedir_com_antecedencia(t2, 5)
    with pytest.raises(ValidationError, match='Deve pedir com pelo menos 2 dias úteis de antecedência'):
        deve_pedir_com_antecedencia(t3, 2)
    with pytest.raises(ValidationError, match='Deve pedir com pelo menos 2 dias úteis de antecedência'):
        deve_pedir_com_antecedencia(t4, 2)


def test_dia_util():
    t1 = datetime.date(2019, 6, 3)
    t2 = datetime.date(2019, 6, 4)
    t3 = datetime.date(2019, 6, 5)
    t4 = datetime.date(2019, 6, 6)
    t5 = datetime.date(2019, 6, 7)
    assert dia_util(t1) is True
    assert dia_util(t2) is True
    assert dia_util(t3) is True
    assert dia_util(t4) is True
    assert dia_util(t5) is True


def test_not_dia_util():
    t1 = datetime.date(2019, 6, 15)  # sab
    t2 = datetime.date(2019, 6, 16)  # dom
    t3 = datetime.date(2019, 6, 20)  # feriado corpus crhist
    t4 = datetime.date(2019, 12, 25)  # qua natal
    with pytest.raises(ValidationError, match='Não é dia útil em São Paulo'):
        dia_util(t1)
    with pytest.raises(ValidationError, match='Não é dia útil em São Paulo'):
        dia_util(t2)
    with pytest.raises(ValidationError, match='Não é dia útil em São Paulo'):
        dia_util(t3)
    with pytest.raises(ValidationError, match='Não é dia útil em São Paulo'):
        dia_util(t4)


@freeze_time("2019-05-22")
def test_nao_pode_ser_passado():
    t1 = datetime.date(2019, 5, 27)
    t2 = datetime.date(2020, 5, 27)
    t3 = datetime.date(2019, 5, 23)
    t4 = datetime.date(2019, 5, 22)
    assert nao_pode_ser_passado(t1) is True
    assert nao_pode_ser_passado(t2) is True
    assert nao_pode_ser_passado(t3) is True
    assert nao_pode_ser_passado(t4) is True


@freeze_time("2019-05-22")
def test_nao_pode_ser_passado_raise_exception():
    t1 = datetime.date(2019, 5, 15)
    t2 = datetime.date(2019, 5, 20)
    t3 = datetime.date(2018, 5, 21)
    t4 = datetime.date(2019, 4, 21)
    with pytest.raises(ValidationError, match='Não pode ser no passado'):
        nao_pode_ser_passado(t1)
    with pytest.raises(ValidationError, match='Não pode ser no passado'):
        nao_pode_ser_passado(t2)
    with pytest.raises(ValidationError, match='Não pode ser no passado'):
        nao_pode_ser_passado(t3)
    with pytest.raises(ValidationError, match='Não pode ser no passado'):
        nao_pode_ser_passado(t4)
