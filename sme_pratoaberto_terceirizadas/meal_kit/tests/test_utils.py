from datetime import datetime

import pytest

from sme_pratoaberto_terceirizadas.meal_kit.utils import datetime_to_string, string_to_date


def test_datetime_to_string():
    date_one = datetime(2019, 1, 1)
    date_two = datetime(2019, 12, 31)
    assert datetime_to_string(date_one) == '01/01/2019'
    assert datetime_to_string(date_two) == '31/12/2019'


def test_datetime_to_string_tratando_excecoes():
    with pytest.raises(AssertionError, match='datetime_obj precisa ser `datetime`'):
        datetime_to_string(1)
    with pytest.raises(AssertionError, match='datetime_obj precisa ser `datetime`'):
        datetime_to_string(datetime(2019, 1, 1).date())


def test_string_to_date():
    date_one = '01/01/2019'
    date_two = '31/12/2019'
    assert string_to_date(date_one) == datetime(2019, 1, 1).date()
    assert string_to_date(date_two) == datetime(2019, 12, 31).date()


def test_string_to_date_tratando_excecoes():
    with pytest.raises(AssertionError, match='date_string precisa ser `string`'):
        string_to_date(1)
    with pytest.raises(AssertionError, match='date_string precisa ser `string`'):
        string_to_date(True)
    with pytest.raises(ValueError, match="time data 'abc' does not match format '%d/%m/%Y"):
        string_to_date('abc')
    with pytest.raises(ValueError, match="time data '20190108' does not match format '%d/%m/%Y"):
        string_to_date('20190108')
