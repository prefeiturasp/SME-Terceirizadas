from datetime import date
from workalendar.america import BrazilSaoPauloCity

calendario = BrazilSaoPauloCity()

def mes_para_faixa(mes_string):
    return (
        date(2020, 10, 1),
        date(2020, 10, 31),
    )

def eh_feriado_ou_fds(data):
    return data.weekday() >= 5 or calendario.is_holiday(data)
