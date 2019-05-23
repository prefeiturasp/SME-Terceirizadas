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


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None,
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    # TODO: ajustqar os parametros, ja que a mensagem vai ser sempre a mesma para
    # um determinado grupo de emails.
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        if html:
            message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)
