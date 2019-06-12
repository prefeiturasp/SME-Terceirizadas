from datetime import datetime
from workalendar.america import BrazilSaoPauloCity

from sme_pratoaberto_terceirizadas.school.models import School
from sme_pratoaberto_terceirizadas.users.models import User

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


def converter_str_para_datetime(str_dia, formato='%Y-%m-%d'):
    try:
        data = datetime.strptime(str_dia, formato)
        return data
    except ValueError:
        return False


def valida_usuario_vinculado_escola(usuario: User):
    return School.objects.filter(users=usuario).exists()
