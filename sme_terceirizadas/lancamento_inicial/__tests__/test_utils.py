from datetime import date

from ..utils import eh_feriado_ou_fds, mes_para_faixa


def test_mes_para_faixa(faixas_de_data):
    (mes, faixa_inicio, faixa_fim) = faixas_de_data
    faixa = mes_para_faixa(mes)
    assert faixa[0] == faixa_inicio
    assert faixa[1] == faixa_fim


def test_eh_feriado_ou_fds():
    assert eh_feriado_ou_fds(date(2020, 10, 5)) is False
    assert eh_feriado_ou_fds(date(2020, 10, 6)) is False
    assert eh_feriado_ou_fds(date(2020, 10, 7)) is False
    assert eh_feriado_ou_fds(date(2020, 10, 8)) is False
    assert eh_feriado_ou_fds(date(2020, 10, 9)) is False
    assert eh_feriado_ou_fds(date(2020, 10, 10)) is True
    assert eh_feriado_ou_fds(date(2020, 10, 11)) is True
    assert eh_feriado_ou_fds(date(2020, 10, 12)) is True
    assert eh_feriado_ou_fds(date(2020, 10, 13)) is False
    assert eh_feriado_ou_fds(date(2020, 10, 14)) is False
