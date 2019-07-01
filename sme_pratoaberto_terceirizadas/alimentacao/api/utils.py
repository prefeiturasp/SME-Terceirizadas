from datetime import datetime
from workalendar.america import BrazilSaoPauloCity

from sme_pratoaberto_terceirizadas.escola.models import Escola, DiretoriaRegional
from sme_pratoaberto_terceirizadas.perfil.models import Usuario
from sme_pratoaberto_terceirizadas.utils import async_envio_email_html_em_massa, enviar_notificacao

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
        return datetime.strptime(str_dia, formato)
    except ValueError:
        return False


def valida_usuario_vinculado_escola(usuario: Usuario):
    return Escola.objects.filter(users=usuario).exists()


def notifica_dres(usuario: Usuario, escola: str, dia_de: str, dia_para: str):
    escola = Escola.objects.get(pk=escola)
    usuarios_dre = DiretoriaRegional.objects.get(school=escola).users.all()
    email_usuarios_dre = DiretoriaRegional.objects.filter(school=escola).values_list('users__email')
    mensagem_notificacao = 'Solicitação de inversão de dia de cardápio para a escola {} do dia {} para o dia: {}'.format(
        escola,
        dia_de,
        dia_para)

    enviar_notificacao(
        usuario,
        usuarios_dre,
        'Solicitação de inversão de dia de cardápio da escola: {}'.format(escola),
        mensagem_notificacao
    )

    async_envio_email_html_em_massa('Solicitação de inversão de dia de cardápio: {}'.format(escola), mensagem_notificacao, '',
                              email_usuarios_dre)
