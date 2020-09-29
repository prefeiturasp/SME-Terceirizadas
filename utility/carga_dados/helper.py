from utility.carga_dados.escola.helper import bcolors


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
    '''
    modelo_campo = dicionario.get(str(modelo_id))
    modelo_dicionario = {campo_unico: modelo_campo}
    if modelo_campo:
        return modelo.objects.get(**modelo_dicionario)
