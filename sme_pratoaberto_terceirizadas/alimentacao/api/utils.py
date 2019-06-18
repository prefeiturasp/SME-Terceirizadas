from datetime import datetime
from workalendar.america import BrazilSaoPauloCity

from sme_pratoaberto_terceirizadas.school.models import School, RegionalDirector
from sme_pratoaberto_terceirizadas.users.models import User
from sme_pratoaberto_terceirizadas.utils import async_send_mass_html_mail, send_notification

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
        if dia.date() == feriado[0]:
            return False
    return True


def converter_str_para_datetime(str_dia, formato='%Y-%m-%d'):
    try:
        return datetime.strptime(str_dia, formato)
    except ValueError:
        return False


def valida_usuario_vinculado_escola(usuario: User):
    return School.objects.filter(users=usuario).exists()


def notifica_dres(usuario: User, escola: School, dia_de: datetime, dia_para: datetime):
    # escola = School.objects.get(pk=escola)
    usuarios_dre = RegionalDirector.objects.get(school=escola).users.all()
    email_usuarios_dre = RegionalDirector.objects.filter(school=escola).values_list('users__email')
    mensagem_notificacao = 'Solicitação de inversão de dia de cardápio para a escola {} do dia {} para o dia: {}'.format(
        escola,
        dia_de.date().strftime('%d/%m/%Y'),
        dia_para.date().strftime('%d/%m/%Y'))

    send_notification(
        usuario,
        usuarios_dre,
        'Solicitação de inversão de dia de cardápio da escola: {}'.format(escola),
        mensagem_notificacao
    )

    async_send_mass_html_mail('Solicitação de inversão de dia de cardápio: {}'.format(escola), mensagem_notificacao, '',
                              email_usuarios_dre)
