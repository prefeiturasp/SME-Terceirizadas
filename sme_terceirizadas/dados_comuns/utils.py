import base64
import datetime
import os
import re
import uuid
from mimetypes import guess_extension, guess_type
from typing import Any

import environ
import numpy as np
from config.settings.base import URL_CONFIGS
from des.models import DynamicEmailConfiguration
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection, send_mail
from workalendar.america import BrazilSaoPauloCity

from .constants import DAQUI_A_SETE_DIAS, DAQUI_A_TRINTA_DIAS, DOMINIOS_DEV
from .models import CentralDeDownload

calendar = BrazilSaoPauloCity()

env = environ.Env()


def eh_email_dev(email):
    for dominio in DOMINIOS_DEV:
        if email.endswith(dominio):
            return True
    return False


def remove_emails_dev(lista_emails, modo_debug=settings.DEBUG):
    """Remove emails que sao usados apenas em desenvolvimento quando a aplicação está em modo produção."""
    if modo_debug:
        return lista_emails

    nova_lista = []
    for email in lista_emails:
        if not eh_email_dev(email):
            nova_lista.append(email)

    return nova_lista


def envia_email_unico(assunto: str, corpo: str, email: str, template: str, dados_template: Any, html=None):
    config = DynamicEmailConfiguration.get_solo()

    return send_mail(
        assunto,
        corpo,
        config.from_email or None,
        [email],
        html_message=html)


def envia_email_unico_com_anexo(assunto: str, corpo: str, email: str, anexo=[]):  # noqa B006
    # Anexa um arquivo no email.
    # Usado em enviar_email_para_diretor_da_escola_destino.
    config = DynamicEmailConfiguration.get_solo()

    email = EmailMessage(
        assunto,
        corpo,
        config.from_email or None,
        [email]
    )
    email.content_subtype = 'html'
    _mimetypes, _ = guess_type(anexo.name)
    # Este anexo vem da pasta media.
    nome_anexo = anexo.name.split('/')[-1]
    nome_anexo = nome_anexo.replace('_auto', '')
    email.attach(nome_anexo, anexo.read(), _mimetypes)
    email.send()


def envia_email_unico_com_anexo_inmemory(assunto: str, corpo: str, email: str, anexo_nome: str, mimetypes: str, anexo=[]):  # noqa E501
    # Rever a obrigatoriedade de anexo_nome e mimetypes para implementações futuras, ou generalização.
    config = DynamicEmailConfiguration.get_solo()

    email = EmailMessage(
        assunto,
        corpo,
        config.from_email or None,
        [email]
    )
    email.content_subtype = 'html'
    email.attach(anexo_nome, anexo, mimetypes)
    email.send()


def envia_email_em_massa(assunto: str, corpo: str, emails: list, template: str, dados_template: Any, html=None):
    config = DynamicEmailConfiguration.get_solo()
    from_email = config.from_email
    with get_connection() as connection:
        messages = []
        for email in remove_emails_dev(emails):
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
    if 'http' in env('REACT_APP_URL'):
        return env('REACT_APP_URL') + URL_CONFIGS[variable].format(**content)
    http_ou_https = 'http://' if ':' in env('REACT_APP_URL') else 'https://'
    return http_ou_https + env('REACT_APP_URL') + URL_CONFIGS[variable].format(**content)


def convert_base64_to_contentfile(base64_str: str):
    format, imgstr = base64_str.split(';base64,')
    if format == 'data:application/vnd.ms-excel':
        ext = '.xls'
    else:
        ext = guess_extension(format[5:]) or ''
    data = ContentFile(base64.b64decode(imgstr), name=str(uuid.uuid4()) + ext)
    return data


def convert_image_to_base64(image_file, format):
    if not os.path.isfile(image_file):
        return None

    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read())
    return 'data:image/%s;base64,%s' % (format, encoded_string.decode('utf-8'))


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


def gera_objeto_na_central_download(user, identificador):
    usuario = get_user_model().objects.get(username=user)
    obj_arquivo_download = CentralDeDownload.objects.create(
        identificador=identificador,
        arquivo=None,
        status=CentralDeDownload.STATUS_EM_PROCESSAMENTO,
        msg_erro='',
        visto=False,
        usuario=usuario
    )
    obj_arquivo_download.save()

    return obj_arquivo_download


def atualiza_central_download(obj_central_download, identificador, arquivo):
    type_pdf = 'application/pdf'
    type_xlsx = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    content_type = type_pdf if '.pdf' in identificador else type_xlsx

    obj_central_download.arquivo = SimpleUploadedFile(identificador, arquivo, content_type=content_type)
    obj_central_download.status = CentralDeDownload.STATUS_CONCLUIDO
    obj_central_download.save()


def atualiza_central_download_com_erro(obj_central_download, msg_erro):
    obj_central_download.status = CentralDeDownload.STATUS_ERRO
    obj_central_download.msg_erro = msg_erro
    obj_central_download.save()


class ExportExcelAction:
    @classmethod # noqa
    def generate_header(cls, admin, model, list_display):
        def default_format(value):
            return value.replace('_', ' ').upper()

        header = []
        for field_display in list_display:
            is_model_field = field_display in [f.name for f in model._meta.fields]
            is_admin_field = hasattr(admin, field_display)
            if is_model_field:
                field = model._meta.get_field(field_display)
                field_name = getattr(field, 'verbose_name', field_display)
                header.append(default_format(field_name))
            elif is_admin_field:
                field = getattr(admin, field_display)
                field_name = getattr(field, 'short_description', default_format(field_display))
                header.append(default_format(field_name))
            else:
                header.append(default_format(field_display))
        return header


def remove_tags_html_from_string(html_string: str):
    return re.sub(r'<.*?>', '', html_string)


def get_ultimo_dia_mes(date: datetime.date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month + 1, day=1) - datetime.timedelta(days=1)


def remove_multiplos_espacos(string: str):
    return ' '.join(string.split())


def build_xlsx_generico(output, queryset_serializada, titulo, subtitulo, titulo_sheet, titulos_colunas):
    LINHA_0 = 0
    LINHA_1 = 1
    LINHA_2 = 2
    LINHA_3 = 3

    ALTURA_COLUNA_30 = 30
    ALTURA_COLUNA_50 = 50

    import pandas as pd
    xlwriter = pd.ExcelWriter(output, engine='xlsxwriter')

    df = pd.DataFrame(queryset_serializada)

    # Adiciona linhas em branco no comeco do arquivo
    df_auxiliar = pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns)
    df = df_auxiliar.append(df, ignore_index=True)
    df = df_auxiliar.append(df, ignore_index=True)
    df = df_auxiliar.append(df, ignore_index=True)

    df.to_excel(xlwriter, titulo_sheet)
    workbook = xlwriter.book
    worksheet = xlwriter.sheets[titulo_sheet]
    worksheet.set_row(LINHA_0, ALTURA_COLUNA_50)
    worksheet.set_row(LINHA_1, ALTURA_COLUNA_30)
    worksheet.set_column('B:H', ALTURA_COLUNA_30)
    merge_format = workbook.add_format({'align': 'center', 'bg_color': '#a9d18e', 'border_color': '#198459'})
    merge_format.set_align('vcenter')
    merge_format.set_bold()
    cell_format = workbook.add_format()
    cell_format.set_text_wrap()
    cell_format.set_align('vcenter')
    cell_format.set_bold()
    v_center_format = workbook.add_format()
    v_center_format.set_align('vcenter')
    single_cell_format = workbook.add_format({'bg_color': '#a9d18e'})
    len_cols = len(df.columns)
    worksheet.merge_range(0, 0, 0, len_cols, titulo, merge_format)

    worksheet.merge_range(LINHA_1, 0, LINHA_2, len_cols, subtitulo, cell_format)
    worksheet.insert_image('A1', 'sme_terceirizadas/static/images/logo-sigpae-light.png')
    for index, titulo_coluna in enumerate(titulos_colunas, start=1):
        worksheet.write(LINHA_3, index, titulo_coluna, single_cell_format)

    df.reset_index(drop=True, inplace=True)
    xlwriter.save()
    output.seek(0)
