import datetime

import environ
from config.settings.base import URL_CONFIGS
from des.models import DynamicEmailConfiguration
from django.core.mail import EmailMultiAlternatives, get_connection, send_mail
from workalendar.america import BrazilSaoPauloCity

calendar = BrazilSaoPauloCity()

env = environ.Env()


def envia_email_unico(assunto: str, corpo: str, email: str, html: str = None):
    config = DynamicEmailConfiguration.get_solo()

    return send_mail(
        assunto,
        corpo,
        config.from_email or None,
        [email],
        html_message=html)


def envia_email_em_massa(assunto: str, corpo: str, emails: list, html: str = None):
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


def url_configs(variable, content):
    # TODO: rever essa logica de link para trabalhar no front, tá dando voltas
    return env('REACT_APP_URL') + URL_CONFIGS[variable].format(**content)
