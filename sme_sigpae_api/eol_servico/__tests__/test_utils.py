from ..utils import dt_nascimento_from_api


def test_utils_dt_nascimento_from_api(datas_nascimento_api):
    (str_dt_nascimento, ano, mes, dia) = datas_nascimento_api
    obj_dt_nascimento = dt_nascimento_from_api(str_dt_nascimento)
    assert obj_dt_nascimento.year == ano
    assert obj_dt_nascimento.month == mes
    assert obj_dt_nascimento.day == dia
