import requests
import environ

env = environ.Env()


def get_informacoes_usuario(registro_funcional):
    headers = {'Authorization': f'Token {env("DJANGO_EOL_API_TOKEN")}'}
    r = requests.get(f'{env("DJANGO_EOL_API_URL")}/cargos/{registro_funcional}', headers=headers)
    return r.json()

