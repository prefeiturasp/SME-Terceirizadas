import environ
import requests

from ..dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL

env = environ.Env()


class EolException(Exception):
    pass


def get_informacoes_usuario(registro_funcional):
    # TODO: melhorar, trazer o outro consumidor da api pra ca (está no app usuário)
    headers = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}
    response = requests.get(f'{DJANGO_EOL_API_URL}/cargos/{registro_funcional}', headers=headers, timeout=5)
    return response
