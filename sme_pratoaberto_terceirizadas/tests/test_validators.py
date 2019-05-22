import datetime

from freezegun import freeze_time
from rest_framework.exceptions import ValidationError

from sme_pratoaberto_terceirizadas.validators import deve_pedir_com_antecedencia, dia_util, nao_pode_ser_passado

test_date = datetime.date(2019, 5, 27)
final_semana = datetime.date(2019, 5, 25)
passado = datetime.date(2000, 1, 1)


@freeze_time("2019-05-22")
def test_deve_pedir_com_antecedencia():
    deve_pedir_com_antecedencia(test_date, 2)
    return True


@freeze_time("2019-05-22")
def test_deve_pedir_com_antecedencia_validation_error():
    try:
        deve_pedir_com_antecedencia(test_date, 5)
    except ValidationError as e:
        assert str(e) == "[ErrorDetail(string='Deve pedir com pelo menos 5 dias úteis de " \
                         "antecedência', code='invalid')]"


def test_dia_util():
    assert dia_util(test_date) is True


def test_final_semana():
    try:
        dia_util(final_semana)
    except ValidationError as e:
        assert str(e) == "[ErrorDetail(string='Não é dia útil em São Paulo', code='invalid')]"


@freeze_time("2019-05-22")
def test_nao_pode_ser_passado():
    assert nao_pode_ser_passado(test_date) is True


@freeze_time("2019-05-22")
def test_nao_pode_ser_passado_raise_exception():
    try:
        nao_pode_ser_passado(passado)
    except ValidationError as e:
        assert str(e) == "[ErrorDetail(string='Não pode ser no passado', code='invalid')]"
