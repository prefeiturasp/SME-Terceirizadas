import environ
import requests
from rest_framework import status

from ..dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL

env = environ.Env()


class EolException(Exception):
    pass


def get_informacoes_usuario(registro_funcional):
    # TODO: melhorar, trazer o outro consumidor da api pra ca (está no app usuário)
    headers = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}
    response = requests.get(f'{DJANGO_EOL_API_URL}/cargos/{registro_funcional}', headers=headers, timeout=5)
    return response


class EOLService(object):

    @classmethod
    def get_informacoes_aluno(cls, codigo_eol):
        """Retorna detalhes do aluno.
        A api do EOL retorna assim:
        {'cd_aluno': 0001234,
          'nm_aluno': 'XXXXXX',
          'nm_social_aluno': None,
          'dt_nascimento_aluno': '1973-08-14T00:00:00',
          'cd_sexo_aluno': 'M',
          'nm_mae_aluno': 'XXXXX',
          'nm_pai_aluno': 'XXXX'}
        """
        headers = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}
        response = requests.get(f'{DJANGO_EOL_API_URL}/alunos/{codigo_eol}', headers=headers, timeout=5)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) == 1:
                return results[0]
            return {}
        else:
            return {}
