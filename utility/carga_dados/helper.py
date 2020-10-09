import csv
import io
import sys
import urllib.request

import xlrd
from utility.carga_dados.escola.helper import bcolors


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size * j / count)
        file.write("%s [%s%s] %i/%i\r" %
                   (prefix, "#" * x, "." * (size - x), j, count))
        file.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()


def somente_digitos(palavra):
    return ''.join(p for p in palavra if p.isdigit())


def csv_to_list(arquivo: str) -> list:
    '''
    Lê um csv e retorna um OrderedDict.
    '''
    with open(arquivo) as f:
        leitor = csv.DictReader(f, delimiter=',')
        dados = [linha for linha in leitor]
    return dados


def csv_online_to_list(url: str) -> list:
    '''
    Lê um CSV a partir de uma url.
    '''
    url_open = urllib.request.urlopen(url)
    leitor = csv.DictReader(io.StringIO(url_open.read().decode('utf-8')), delimiter=',')  # noqa
    dados = [linha for linha in leitor]
    return dados


def excel_to_list(arquivo, in_memory=False):
    '''
    Lê planilha Excel e retorna uma lista de dicionários.
    Você pode informar se quer ler o arquivo InMemoryUploadedFile.
    https://stackoverflow.com/a/38309568/802542
    https://stackoverflow.com/a/12886981/802542
    '''
    if in_memory:
        workbook = xlrd.open_workbook(filename=arquivo, file_contents=arquivo.read())  # noqa
    else:
        workbook = xlrd.open_workbook(arquivo)
    sheet = workbook.sheet_by_index(0)

    primeira_linha = []
    for col in range(sheet.ncols):
        primeira_linha.append(sheet.cell_value(0, col).strip())

    dados = []
    for row in range(1, sheet.nrows):
        objeto = {}
        for col in range(sheet.ncols):
            objeto[primeira_linha[col]] = sheet.cell_value(row, col)
        dados.append(objeto)
    return dados


def ja_existe(model, item):
    print(f'{bcolors.FAIL}Aviso: {model}: "{item}" já existe!{bcolors.ENDC}')


def le_dados(items, campo_unico='nome'):
    '''
    Lê os dados para extrair id e um outro campo como identificador único
    e monta um dicionário.
    '''
    dicionario = {}
    for item in items:
        dicionario[str(item['id'])] = item[campo_unico]
    return dicionario


def get_modelo(modelo, modelo_id, dicionario, campo_unico):
    '''
    Retorna uma modelo.

    Args:
        modelo (str): Modelo onde vai procurar o valor.
        modelo_id (int): id do moelo.
        dicionario (dict): Dicionário onde vai procurar o valor.
        campo_unico (str): Nome do campo que define o valor como único.
    '''
    modelo_campo = dicionario.get(str(modelo_id))
    modelo_dicionario = {campo_unico: modelo_campo}
    if modelo_campo:
        return modelo.objects.get(**modelo_dicionario)


def adiciona_m2m_items(campo_m2m, dicionario_m2m, modelo, dicionario, campo_unico):  # noqa
    '''
    Adiciona os items na relação many to many.

    Args:
        campo_m2m: Nome do campo da relação many to many.
        dicionario_m2m: Dicionário com os valores many to many.
        modelo (str): Modelo onde vai procurar o valor.
        dicionario (dict): Dicionário onde vai procurar o valor.
        campo_unico (str): Nome do campo que define o valor como único.
    '''
    for id in dicionario_m2m:
        obj = get_modelo(
            modelo=modelo,
            modelo_id=id,
            dicionario=dicionario,
            campo_unico=campo_unico
        )
        campo_m2m.add(obj)
