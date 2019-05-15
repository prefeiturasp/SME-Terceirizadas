from datetime import datetime
from workalendar.america import BrazilSaoPauloCity


def str_to_date(date_str, format_date_str='%d/%m/%Y'):
    """
    Auxilliary method to define format to send and receive dates
    """
    try:
        return datetime.strptime(date_str, format_date_str).date()
    except ValueError:
        raise Exception('invalid_date')


def get_working_days_after(days=5, date=datetime.utcnow().date()):
    """Retorna o próximo dia útil após a variável days"""
    calendar = BrazilSaoPauloCity()
    return calendar.add_working_days(date, days)
