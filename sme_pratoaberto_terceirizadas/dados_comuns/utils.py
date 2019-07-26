import datetime

from des.models import DynamicEmailConfiguration
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.mail import send_mail
from django.db.models import QuerySet
from notifications.signals import notify
from workalendar.america import BrazilSaoPauloCity

from sme_pratoaberto_terceirizadas.perfil.models import Usuario

calendar = BrazilSaoPauloCity()


def enviar_notificacao(sender: Usuario, recipient: [QuerySet, list],
                       short_desc: str, long_desc: str):
    """
    :param sender: User instance
    :param recipient: A Group or User QuerySet or User List
    :param short_desc:
    :param long_desc:
    """
    notify.send(
        sender=sender,
        recipient=recipient,
        verb=short_desc,
        description=long_desc
    )


def send_email(subject, message_text, to_email):
    config = DynamicEmailConfiguration.get_solo()
    send_mail(
        subject,
        message_text,
        config.from_email or None,
        [to_email])


def _send_mass_html_mail(subject, text, html, recipients):
    """
    :param subject:
    :param text:
    :param html:
    :param recipients: an array of email
    :return:
    """
    config = DynamicEmailConfiguration.get_solo()
    from_email = config.from_email

    connection = get_connection()

    messages = []
    for recipient in recipients:
        message = EmailMultiAlternatives(subject, text, from_email, [recipient])
        if html:
            message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)


# loop = asyncio.get_event_loop()


def async_envio_email_html_em_massa(subject, text, html, recipients):
    pass
    # loop.run_in_executor(None, _send_mass_html_mail, subject, text, html, recipients)


def obter_dias_uteis_apos_hoje(quantidade_dias: int):
    """Retorna o próximo dia útil após quantidade_dias"""
    dia = datetime.date.today()

    return calendar.add_working_days(dia, quantidade_dias)


def eh_dia_util(date):
    return calendar.is_working_day(date)


def update_instance_from_dict(instance, attrs):
    for attr, val in attrs.items():
        setattr(instance, attr, val)
    return instance
