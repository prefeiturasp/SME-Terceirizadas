import environ
from freezegun import freeze_time

from ..constants import (
    DAQUI_A_SETE_DIAS,
    DAQUI_A_TRINTA_DIAS,
    SEM_FILTRO,
    obter_dias_uteis_apos_hoje,
)
from ..utils import queryset_por_data, update_instance_from_dict

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
