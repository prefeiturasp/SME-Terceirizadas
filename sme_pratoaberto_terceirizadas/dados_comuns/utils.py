import datetime

from workalendar.america import BrazilSaoPauloCity

calendar = BrazilSaoPauloCity()


def string_para_data(data_string: str, formato_data_string='%d/%m/%Y'):
    """
    Auxilliary method to define format to send and receive dates
    """
    try:
        return datetime.datetime.strptime(data_string, formato_data_string).date()
    except (ValueError, AttributeError):
        raise Exception('data invalida')


def obter_dias_uteis_apos(days=2, date=datetime.datetime.now()):
    """Retorna o próximo dia útil após a variável days"""
    return calendar.add_working_days(date, days)


def eh_dia_util(date):
    return calendar.eh_dia_util(date)
