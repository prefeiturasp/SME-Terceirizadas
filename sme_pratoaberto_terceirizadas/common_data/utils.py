import datetime

from workalendar.america import BrazilSaoPauloCity

calendar = BrazilSaoPauloCity()


def str_to_date(date_str: str, format_date_str='%d/%m/%Y'):
    """
    Auxilliary method to define format to send and receive dates
    """
    try:
        return datetime.datetime.strptime(date_str, format_date_str).date()
    except (ValueError, AttributeError):
        raise Exception('invalid_date')


def get_working_days_after(days=2, date=datetime.datetime.now()):
    """Retorna o próximo dia útil após a variável days"""
    return calendar.add_working_days(date, days)


def is_working_day(date):
    return calendar.is_working_day(date)
