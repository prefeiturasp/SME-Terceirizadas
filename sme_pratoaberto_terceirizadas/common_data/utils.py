from datetime import datetime


def str_to_date(date_str, format_date_str='%d%m%Y'):
    """
    Auxilliary method to define format to send and receive dates
    """
    try:
        return datetime.strptime(date_str, format_date_str).date()
    except ValueError:
        raise Exception('invalid_date')
