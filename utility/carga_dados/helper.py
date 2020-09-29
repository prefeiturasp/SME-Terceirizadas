import sys
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
