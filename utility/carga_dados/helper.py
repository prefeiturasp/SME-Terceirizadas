from utility.carga_dados.escola.helper import bcolors


def ja_existe(model, item):
    print(f'{bcolors.FAIL}Aviso: {model}: "{item}" já existe!{bcolors.ENDC}')
