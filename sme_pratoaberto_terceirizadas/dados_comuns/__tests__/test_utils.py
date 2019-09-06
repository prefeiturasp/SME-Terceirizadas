from freezegun import freeze_time

from sme_pratoaberto_terceirizadas.dados_comuns.utils import obter_dias_uteis_apos_hoje, update_instance_from_dict


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
