import environ
import requests
from rest_framework import status

from ..dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL

env = environ.Env()


class EOLException(Exception):
    pass


class EOLService(object):
    DEFAULT_HEADERS = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}
    DEFAULT_TIMEOUT = 5

    @classmethod
    def get_informacoes_usuario(cls, registro_funcional):
        """Retorna detalhes de vínculo de um RF.

        mostra todos os vínculos desse RF. EX: fulano é diretor em AAAA e ciclano é professor em BBBB.
            {
        "results": [
            {
                "nm_pessoa": "XXXXXXXX",
                "cd_cpf_pessoa": "000.000.000-00",
                "cargo": "ANALISTA DE SAUDE NIVEL I",
                "divisao": "NUCLEO DE SUPERVISAO DA ALIMENT ESCOLAR - CODAE-DINUTRE-NSAE",
                "coord": null
            }
            ]
            }
        """
        response = requests.get(f'{DJANGO_EOL_API_URL}/cargos/{registro_funcional}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) >= 1:
                return results
            raise EOLException(f'Resultados para o RF: {registro_funcional} vazios')
        else:
            raise EOLException(f'API EOL com erro. Status: {response.status_code}')

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
        response = requests.get(f'{DJANGO_EOL_API_URL}/alunos/{codigo_eol}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)

        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) == 1:
                return results[0]
            raise EOLException(f'Resultados para o código: {codigo_eol} vazios')
        else:
            raise EOLException(f'API EOL com erro. Status: {response.status_code}')
