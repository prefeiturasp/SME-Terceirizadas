#
# send_email.py  - Usa SSL
#

import smtplib
import ssl
import mimetypes
import ntpath

from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

# ..Parametros - email account criado para testes
sender_address = ''
password = ''
default_subject = 'Testando envio de email {}'.format(sender_address)
smtp_server_address = "smtp.gmail.com"
smtp_port_number = 465


def send_by_smtp(to=None, cc=None, bcc=None, subject=None, texto=None, html=None, attachments=None):
    email_from = sender_address
    email_to = list()
    files_to_send = attachments
    msg = MIMEMultipart("alternative")
    msg["From"] = email_from

    if to:
        to = list(set(to))
        email_to += to
        msg["To"] = ', '.join(to)
    if cc:
        cc = list(set(cc))
        email_to += cc
        msg["Cc"] = ', '.join(cc)
    if bcc:
        bcc = list(set(bcc))
        email_to += bcc
        msg["Bcc"] = ', '.join(bcc)
    if subject:
        msg["Subject"] = subject
        msg.preamble = subject
    else:
        msg["Subject"] = default_subject
        msg.preamble = default_subject

    msg.attach(MIMEText(texto, "plain"))
    msg.attach(MIMEText(html, "html"))

    if files_to_send:
        for file_to_send in files_to_send:
            content_type, encoding = mimetypes.guess_type(file_to_send)
            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"
            maintype, subtype = content_type.split("/", 1)
            if maintype == "text":
                with open(file_to_send) as fp:
                    attachment = MIMEText(fp.read(), _subtype=subtype)
            elif maintype == "image":
                with open(file_to_send, "rb") as fp:
                    attachment = MIMEImage(fp.read(), _subtype=subtype)
            elif maintype == "audio":
                with open(file_to_send, "rb")as fp:
                    attachment = MIMEAudio(fp.read(), _subtype=subtype)
            else:
                with open(file_to_send, "rb") as fp:
                    attachment = MIMEBase(maintype, subtype)
                    attachment.set_payload(fp.read())
                encoders.encode_base64(attachment)

            attachment.add_header("Content-Disposition", "attachment", filename=ntpath.basename(file_to_send))
            msg.attach(attachment)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host=smtp_server_address, port=smtp_port_number, context=context, timeout=300) as server:
            server.login(sender_address, password)
            server.sendmail(from_addr=email_from, to_addrs=email_to, msg=msg.as_string())
        print('Email enviado para: {}'.format(str(email_to)))
        return True
    except smtplib.SMTPException as e:
        print('Error: falha no envio do email.')
        print(e)
        return False


if __name__ == '__main__':
    texto = """\
    Olá,

    seguem anexados os arquivos requisitados.
    Clique www.amcom.com.br para obeter mais informação sobre nós.

    Saudações,
    Jaime
    """

    html = """\
    <html>
      <body>
        <p>Olá,</p>
        <p>seguem anexados os arquivos requisitados.</p>
        <p>Clique <strong><a href="https://amcom.com.br/">aqui</a></strong> para obeter mais informações sobre nós.</p>
        <p>Saudações,</p>
        <p>Jaime</p>
      </body>
    </html>
    """

    print('Enviado email..')
    result = send_by_smtp(to=[''],
                          cc=[''],
                          bcc=[],
                          subject='',
                          texto=texto,
                          html=html,
                          attachments=[''])


    if result:
        print('Email enviado com sucesso.')
    else:
        print('Email não pudo ser enviado.')
