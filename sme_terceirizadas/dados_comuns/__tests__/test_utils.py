import environ
from freezegun import freeze_time

from ..utils import obter_dias_uteis_apos_hoje, update_instance_from_dict, url_configs

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


def test_url_configs():
    variable = 'CONFIRMAR_EMAIL'
    content = {'uuid': '123', 'confirmation_key': '!@#$%'}
    assert url_configs(variable, content) == (env('REACT_APP_URL') +
                                              '/confirmar-email?uuid=123&confirmationKey=!@#$%')
