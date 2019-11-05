import asyncio
import datetime

import environ
from des.models import DynamicEmailConfiguration
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail import send_mail
from django.db.models import QuerySet
from workalendar.america import BrazilSaoPauloCity

from config.settings.base import URL_CONFIGS

calendar = BrazilSaoPauloCity()

env = environ.Env()


def send_email(subject, message_text, to_email):
    config = DynamicEmailConfiguration.get_solo()
    send_mail(
        subject,
        message_text,
        config.from_email or None,
        [to_email])


def _send_mass_html_mail(subject, text, html, recipients):
    """Envia email em massa.

    :param subject:
    :param text:
    :param html:
    :param recipients: an array of User
    :return:
    """
    config = DynamicEmailConfiguration.get_solo()
    from_email = config.from_email

    with get_connection() as connection:
        messages = []
        for recipient in recipients:
            message = EmailMultiAlternatives(subject, text, from_email, [recipient.email])
            if html:
                message.attach_alternative(html, 'text/html')
            messages.append(message)
        return connection.send_messages(messages)


loop = asyncio.get_event_loop()


async def async_envio_email_html_em_massa(subject, text, html, recipients):
    if not recipients:
        return
    await loop.run_in_executor(None, _send_mass_html_mail, subject, text, html, recipients)


def obter_dias_uteis_apos_hoje(quantidade_dias: int):
    """Retorna o próximo dia útil após quantidade_dias."""
    dia = datetime.date.today()

    return calendar.add_working_days(dia, quantidade_dias)


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


def enviar_notificacao_e_email(sender, recipients: QuerySet,
                               short_desc: str, long_desc: str):
    async_envio_email_html_em_massa(subject=short_desc, text='', html=long_desc, recipients=recipients)


def url_configs(variable, content):
    return env('REACT_APP_URL') + URL_CONFIGS[variable].format(**content)
