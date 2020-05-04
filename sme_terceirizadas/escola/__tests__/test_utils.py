from ..utils import meses_para_mes_e_ano_string


def test_meses_para_mes_e_ano_string():
    assert meses_para_mes_e_ano_string(0) == '0 meses'
    assert meses_para_mes_e_ano_string(1) == '1 mês'
    assert meses_para_mes_e_ano_string(2) == '2 meses'
    assert meses_para_mes_e_ano_string(3) == '3 meses'
    assert meses_para_mes_e_ano_string(11) == '11 meses'
    assert meses_para_mes_e_ano_string(12) == '1 ano'
    assert meses_para_mes_e_ano_string(13) == '1 ano e 1 mês'
    assert meses_para_mes_e_ano_string(14) == '1 ano e 2 meses'
    assert meses_para_mes_e_ano_string(15) == '1 ano e 3 meses'
    assert meses_para_mes_e_ano_string(23) == '1 ano e 11 meses'
    assert meses_para_mes_e_ano_string(24) == '2 anos'
    assert meses_para_mes_e_ano_string(25) == '2 anos e 1 mês'
    assert meses_para_mes_e_ano_string(26) == '2 anos e 2 meses'
    assert meses_para_mes_e_ano_string(27) == '2 anos e 3 meses'
    assert meses_para_mes_e_ano_string(35) == '2 anos e 11 meses'
    assert meses_para_mes_e_ano_string(36) == '3 anos'
