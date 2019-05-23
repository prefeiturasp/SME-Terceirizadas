from des.models import DynamicEmailConfiguration
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.mail import send_mail
from django.db.models import QuerySet
from notifications.signals import notify

from sme_pratoaberto_terceirizadas.users.models import User


def send_notification(sender: User, recipients: [QuerySet, list],
                      short_desc: str, long_desc: str):
    """
    :param sender: User instance
    :param recipients: A Group or User QuerySet or User List
    :param short_desc:
    :param long_desc:
    """
    notify.send(
        sender=sender,
        recipient=recipients,
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


def send_mass_html_mail(subject, text, html, recipients):
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
