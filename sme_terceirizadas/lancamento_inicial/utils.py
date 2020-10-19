from calendar import monthrange
from datetime import date

from workalendar.america import BrazilSaoPauloCity


def mes_para_faixa(mes_string):
    (mes, ano) = mes_string.split('/')
    mes = int(mes)
    ano = int(ano)
    ultimo_dia_do_mes = monthrange(ano, mes)[1]
    return (
        date(ano, mes, 1),
        date(ano, mes, ultimo_dia_do_mes),
    )


def eh_feriado_ou_fds(data):
    calendario = BrazilSaoPauloCity()
    return data.weekday() >= 5 or calendario.is_holiday(data)
