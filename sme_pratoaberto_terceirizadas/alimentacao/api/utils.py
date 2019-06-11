from datetime import datetime
from workalendar.america import BrazilSaoPauloCity

calendar = BrazilSaoPauloCity()


def valida_dia_util(dia):
    fim_de_semana = [5, 6]
    dia_semana = dia.weekday()
    if dia_semana in fim_de_semana:
        return False
    return True


def valida_dia_feriado(dia):
    feriados = calendar.get_variable_days(dia.year)
    for feriado in feriados:
        if dia == feriado[0]:
            return False
    return True
