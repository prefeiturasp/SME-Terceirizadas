import base64
import datetime
import uuid
from mimetypes import guess_extension
from typing import Any

import environ
from config.settings.base import URL_CONFIGS
from des.models import DynamicEmailConfiguration
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives, get_connection, send_mail
from workalendar.america import BrazilSaoPauloCity

from .constants import DAQUI_A_SETE_DIAS, DAQUI_A_TRINTA_DIAS

calendar = BrazilSaoPauloCity()

env = environ.Env()


def envia_email_unico(assunto: str, corpo: str, email: str, template: str, dados_template: Any, html=None):
    config = DynamicEmailConfiguration.get_solo()

    return send_mail(
        assunto,
        corpo,
        config.from_email or None,
        [email],
        html_message=html)


def envia_email_em_massa(assunto: str, corpo: str, emails: list, template: str, dados_template: Any, html=None):
    config = DynamicEmailConfiguration.get_solo()
    from_email = config.from_email
    with get_connection() as connection:
        messages = []
        for email in emails:
            message = EmailMultiAlternatives(assunto, corpo, from_email, [email])
            if html:
                message.attach_alternative(html, 'text/html')
            messages.append(message)
        return connection.send_messages(messages)


def obter_dias_uteis_apos(dia: datetime.date, quantidade_dias: int):
    """Retorna o próximo dia útil após dia de parâmetro."""
    return calendar.add_working_days(dia, quantidade_dias)


def eh_dia_util(date):
    return calendar.is_working_day(date)


def update_instance_from_dict(instance, attrs, save=False):
    for attr, val in attrs.items():
        setattr(instance, attr, val)
    if save:
        instance.save()
    return instance


def url_configs(variable, content):
    # TODO: rever essa logica de link para trabalhar no front, tá dando voltas
    return env('REACT_APP_URL') + URL_CONFIGS[variable].format(**content)


def convert_base64_to_contentfile(base64_str: str):
    format, imgstr = base64_str.split(';base64,')
    ext = guess_extension(format[5:]) or ''
    data = ContentFile(base64.b64decode(imgstr), name=str(uuid.uuid4()) + ext)
    return data


def queryset_por_data(filtro_aplicado, model):
    if filtro_aplicado == DAQUI_A_SETE_DIAS:
        return model.desta_semana
    elif filtro_aplicado == DAQUI_A_TRINTA_DIAS:
        return model.deste_mes  # type: ignore
    return model.objects  # type: ignore


def convert_date_format(date, from_format, to_format):
    return datetime.datetime.strftime(datetime.datetime.strptime(date, from_format), to_format)


def size(b64string):
    return (len(b64string) * 3) / 4 - b64string.count('=', -2)


ULTIMO_DIA_DO_MES = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}


def subtrai_meses_de_data(meses, data):
    sub_anos = meses // 12
    sub_meses = meses % 12
    if data.month <= sub_meses:
        novo_ano = data.year - (sub_anos + 1)
        novo_mes = 12 - (sub_meses - data.month)
    else:
        novo_ano = data.year - sub_anos
        novo_mes = data.month - sub_meses
    if novo_ano % 20 == 0 and novo_mes == 2 and data.day > 29:
        novo_dia = 29
    elif data.day > ULTIMO_DIA_DO_MES[novo_mes]:
        novo_dia = ULTIMO_DIA_DO_MES[novo_mes]
    else:
        novo_dia = data.day
    return datetime.date(novo_ano, novo_mes, novo_dia)


def ordena_dias_semana_comeca_domingo(dias_semana):
    """
    Obtém uma lista de inteiros onde cada inteiro representa um dia da semana.

    No python, os dias da semana são
    - 0 = Segunda-feira
    - 1 = Terça-feira
    - ...
    - 6 = Domingo

    A função retorna uma lista de inteiros ordenados sendo que o número 6 sempre será o primeiro número.
    """
    return sorted(dias_semana, key=lambda x: -1 if x == 6 else x)
