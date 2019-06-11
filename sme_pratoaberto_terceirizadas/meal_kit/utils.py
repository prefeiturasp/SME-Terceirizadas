import datetime


def datetime_to_string(datetime_obj) -> str:
    return datetime_obj.strftime("%d/%m/%Y")


def string_to_date(date_string: str) -> datetime.date:
    assert isinstance(date_string, str), 'date_string precisa ser `string`'
    return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()
