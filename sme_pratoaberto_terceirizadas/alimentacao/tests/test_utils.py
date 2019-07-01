import pytest
from sme_pratoaberto_terceirizadas.alimentacao.api.utils import *

pytestmark = pytest.mark.django_db


def test_valida_dia_util():
    assert valida_dia_util(datetime(2019, 6, 14))
    assert not valida_dia_util(datetime(2019, 6, 15))


def test_valida_dia_feriado():
    assert valida_dia_feriado(datetime(2019, 6, 20))
    assert not valida_dia_feriado(datetime(2019, 6, 15))


def test_valida_conversao_string_para_datetime():
    assert type(converter_str_para_datetime('2019-06-11')) == datetime
    assert not converter_str_para_datetime('20190611')


def test_validacao_se_usuario_tem_relacionamento_com_escola(usuario_sem_escola):
    assert not valida_usuario_vinculado_escola(usuario_sem_escola)
