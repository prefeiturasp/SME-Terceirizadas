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


def obter_dias_uteis_apos_hoje(quantidade_dias: int):
    """Retorna o próximo dia útil após quantidade_dias"""
    dia = datetime.date.today()

    return calendar.add_working_days(dia, quantidade_dias)


def eh_dia_util(date):
    return calendar.is_working_day(date)


def update_instance_from_dict(instance, attrs):
    for attr, val in attrs.items():
        setattr(instance, attr, val)
    return instance
