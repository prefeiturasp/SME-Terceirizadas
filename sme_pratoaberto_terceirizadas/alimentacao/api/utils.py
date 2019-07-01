from datetime import datetime
from workalendar.america import BrazilSaoPauloCity

from sme_pratoaberto_terceirizadas.school.models import School, RegionalDirector
from sme_pratoaberto_terceirizadas.users.models import User
from sme_pratoaberto_terceirizadas.utils import async_send_mass_html_mail, send_notification

calendar = BrazilSaoPauloCity()


def valida_dia_util(dia):
    return calendar.is_working_day(dia)


def valida_dia_feriado(dia):
    feriado = calendar.is_holiday(dia)
    return feriado


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
        dia_de.strftime('%d/%m/%Y'),
        dia_para.strftime('%d/%m/%Y'))

    send_notification(
        usuario,
        usuarios_dre,
        'Solicitação de inversão de dia de cardápio da escola: {}'.format(escola),
        mensagem_notificacao
    )

    async_send_mass_html_mail('Solicitação de inversão de dia de cardápio: {}'.format(escola), mensagem_notificacao, '',
                              email_usuarios_dre)
