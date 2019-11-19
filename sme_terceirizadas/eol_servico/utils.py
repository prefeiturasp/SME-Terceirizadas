import environ
import requests

from ..dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL

env = environ.Env()


def get_informacoes_usuario(registro_funcional):
    headers = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}
    response = requests.get(f'{DJANGO_EOL_API_URL}/cargos/{registro_funcional}', headers=headers, timeout=5)
    return response
