from datetime import date

import environ
from freezegun import freeze_time

from ..constants import DAQUI_A_SETE_DIAS, DAQUI_A_TRINTA_DIAS, SEM_FILTRO, obter_dias_uteis_apos_hoje
from ..utils import (
    ordena_dias_semana_comeca_domingo,
    queryset_por_data,
    subtrai_meses_de_data,
    update_instance_from_dict
)

env = environ.Env()


@freeze_time('2019-07-10')
def test_obter_dias_uteis_apos(dias_uteis_apos):
    dias, dia_esperado = dias_uteis_apos
    assert obter_dias_uteis_apos_hoje(dias) == dia_esperado


class A(object):
    attribute1 = ''
    attribute2 = ''

    def __str__(self):
        return f'{self.attribute1},{self.attribute2}'


def test_update_instance_from_dict():
    a = A()
    update_instance_from_dict(a, dict(attribute1='xxx', attribute2='yyy'))
    assert a.__str__() == 'xxx,yyy'


class Model(object):
    desta_semana = 0
    deste_mes = 1
    objects = 2


def test_queryset_por_data():
    model = Model()
    assert queryset_por_data(DAQUI_A_SETE_DIAS, model) == model.desta_semana
    assert queryset_por_data(DAQUI_A_TRINTA_DIAS, model) == model.deste_mes
    assert queryset_por_data(SEM_FILTRO, model) == model.objects


def test_subtrai_meses_de_data():
    data_nova = subtrai_meses_de_data(6, date(2020, 3, 15))
    assert data_nova.year == 2019
    assert data_nova.month == 9
    assert data_nova.day == 15
    data_nova = subtrai_meses_de_data(5, date(2020, 6, 15))
    assert data_nova.year == 2020
    assert data_nova.month == 1
    assert data_nova.day == 15
    data_nova = subtrai_meses_de_data(6, date(2020, 6, 15))
    assert data_nova.year == 2019
    assert data_nova.month == 12
    assert data_nova.day == 15
    data_nova = subtrai_meses_de_data(1, date(2020, 3, 30))
    assert data_nova.year == 2020
    assert data_nova.month == 2
    assert data_nova.day == 29
    data_nova = subtrai_meses_de_data(4, date(2020, 3, 31))
    assert data_nova.year == 2019
    assert data_nova.month == 11
    assert data_nova.day == 30
    data_nova = subtrai_meses_de_data(1, date(2019, 3, 30))
    assert data_nova.year == 2019
    assert data_nova.month == 2
    assert data_nova.day == 28
    data_nova = subtrai_meses_de_data(1, date(2020, 5, 31))
    assert data_nova.year == 2020
    assert data_nova.month == 4
    assert data_nova.day == 30


def test_ordena_dias_semana_comeca_domingo():
    dias1 = [3, 0, 5, 2]
    resultado1 = ordena_dias_semana_comeca_domingo(dias1)
    assert resultado1 == [0, 2, 3, 5]

    dias2 = [0, 4, 6, 2]
    resultado2 = ordena_dias_semana_comeca_domingo(dias2)
    assert resultado2 == [6, 0, 2, 4]

    dias3 = [5, 3, 6, 2]
    resultado3 = ordena_dias_semana_comeca_domingo(dias3)
    assert resultado3 == [6, 2, 3, 5]
