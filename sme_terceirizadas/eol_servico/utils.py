from datetime import date

import environ
import requests
from rest_framework import status

from ..dados_comuns.constants import (
    DJANGO_EOL_API_TOKEN,
    DJANGO_EOL_API_URL,
    DJANGO_EOL_PAPA_API_SENHA_CANCELAMENTO,
    DJANGO_EOL_PAPA_API_SENHA_ENVIO,
    DJANGO_EOL_PAPA_API_URL,
    DJANGO_EOL_PAPA_API_USUARIO,
    DJANGO_EOL_SGP_API_TOKEN,
    DJANGO_EOL_SGP_API_URL
)

env = environ.Env()


class EOLException(Exception):
    pass


class EOLService(object):
    DEFAULT_HEADERS = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}
    DEFAULT_TIMEOUT = 20

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
            raise EOLException(f'API do EOL não retornou nada para o RF: {registro_funcional}')
        else:
            raise EOLException(f'API EOL com erro. Status: {response.status_code}')

    @classmethod
    def get_informacoes_aluno(cls, codigo_eol):
        """Retorna detalhes do aluno.

        A api do EOL retorna assim:
        {
            'cd_aluno': 0001234,
            'nm_aluno': 'XXXXXX',
            'nm_social_aluno': None,
            'dt_nascimento_aluno': '1973-08-14T00:00:00',
            'cd_sexo_aluno': 'M',
            'nm_mae_aluno': 'XXXXX',
            'nm_pai_aluno': 'XXXX',
            "cd_escola": "017981",
            "dc_turma_escola": "4C",
            "dc_tipo_turno": "Manhã               "
        }
        """
        response = requests.get(f'{DJANGO_EOL_API_URL}/alunos/{codigo_eol}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)

        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) > 0:
                return results[0]
            raise EOLException(f'Resultados para o código: {codigo_eol} vazios')
        else:
            raise EOLException(f'API EOL com erro. Status: {response.status_code}')

    @classmethod
    def get_informacoes_escola_turma_aluno(cls, codigo_eol):
        """Retorna uma lista de alunos da escola.

        Exemplo de retorno:
        [
            {
                "cod_dre": "109300",
                "sg_dre": "DRE - MP",
                "dre": "DIRETORIA REGIONAL DE EDUCACAO SAO MIGUEL",
                "cd_turma_escola": 2115958,
                "dc_turma_escola": "1A",
                "dc_serie_ensino": "1º Ano",
                "dc_tipo_turno": "Manhã               ",
                "cd_aluno": 6116689,
                "dt_nascimento_aluno": "2013-06-18T00:00:00"
            },
            {...dados de outro aluno},
            {...dados de outro aluno},
            ...
        ]
        """
        response = requests.get(f'{DJANGO_EOL_API_URL}/escola_turma_aluno/{codigo_eol}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)

        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) == 0:
                raise EOLException(f'Resultados para o código: {codigo_eol} vazios')
            return results
        else:
            raise EOLException(f'API EOL com erro. Status: {response.status_code}')


class EOLServicoSGP:
    HEADER = {
        'x-api-eol-key': f'{DJANGO_EOL_SGP_API_TOKEN}'
    }
    TIMEOUT = 10

    @classmethod
    def matricula_por_escola(cls, codigo_eol: str, data: str, tipo_turma: int = 1):
        """Consulta a quantidade de matriculados na API do sgp."""
        response = requests.get(f'{DJANGO_EOL_SGP_API_URL}/matriculas/escolas/dre/{codigo_eol}/quantidades/',
                                headers=cls.HEADER, timeout=cls.TIMEOUT, params={'data': data, 'tipoTurma': tipo_turma})
        if response.status_code == status.HTTP_200_OK:
            resultado = response.json()
            return resultado
        else:
            raise EOLException(f'API EOL do SGP está com erro. Erro: {str(response)}, Status: {response.status_code}')


class EOLPapaService:
    TIMEOUT = 20

    @classmethod
    def confirmacao_de_cancelamento(cls, cnpj, numero_solicitacao, sequencia_envio):
        payload = {
            'CNPJ_PREST': cnpj,
            'NUM_SOL': numero_solicitacao,
            'SEQ_ENVIO': sequencia_envio,
            'USUARIO': DJANGO_EOL_PAPA_API_USUARIO,
            'SENHA': DJANGO_EOL_PAPA_API_SENHA_CANCELAMENTO,

        }

        response = requests.post(f'{DJANGO_EOL_PAPA_API_URL}/confirmarcancelamentosolicitacao/',
                                 timeout=cls.TIMEOUT, json=payload)
        if response.status_code == status.HTTP_200_OK:
            result = response.json()
            if result['RETORNO'] != 'TRUE':
                raise EOLException(
                    f'API EOL do PAPA não confirmou cancelamento. MSG: {str(result)}')
        else:
            raise EOLException(f'API EOL do PAPA está com erro. Erro: {str(response)}, Status: {response.status_code}')

    @classmethod
    def confirmacao_de_envio(cls, cnpj, numero_solicitacao, sequencia_envio):
        if sequencia_envio is None:
            sequencia_envio = 0
        payload = {
            'CNPJ_PREST': cnpj,
            'NUM_SOL': numero_solicitacao,
            'SEQ_ENVIO': sequencia_envio,
            'USUARIO': DJANGO_EOL_PAPA_API_USUARIO,
            'SENHA': DJANGO_EOL_PAPA_API_SENHA_ENVIO,

        }
        response = requests.post(f'{DJANGO_EOL_PAPA_API_URL}/confirmarenviosolicitacao/',
                                 timeout=cls.TIMEOUT, json=payload)
        if response.status_code == status.HTTP_200_OK:
            result = response.json()
            if result['RETORNO'] != 'TRUE':
                raise EOLException(
                    f'API EOL do PAPA não confirmou o envio. MSG: {str(result)}')
        else:
            raise EOLException(f'API EOL do PAPA está com erro. Erro: {str(response)}, Status: {response.status_code}')


def dt_nascimento_from_api(string_dt_nascimento):
    (ano, mes, dia) = string_dt_nascimento.split('T')[0].split('-')
    return date(int(ano), int(mes), int(dia))
