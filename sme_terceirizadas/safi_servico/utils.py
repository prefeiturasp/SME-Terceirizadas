
import requests
from rest_framework import status

from ..dados_comuns.constants import DJANGO_SAFI_API_TOKEN, DJANGO_SAFI_API_URL


class SAFIException(Exception):
    pass


class SAFIService(object):
    DEFAULT_HEADERS = {'Authorization': f'Token {DJANGO_SAFI_API_TOKEN}'}
    DEFAULT_TIMEOUT = 20

    @classmethod
    def get_termos_de_contratos(cls):
        """Retorna termos de contratos e seus respectivos uuid`s.

        [
            {
                "uuid": "abb9bc5d-7d3b-4a11-a0af-89c9ba2bcde3",
                "termo_contrato": "15/SME/CODAE/2022"
            },
        ]
        """
        response = requests.get(f'{DJANGO_SAFI_API_URL}/contratos-sigpae/termos-de-contratos/',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            resultado = response.json()
            if resultado:
                return resultado
            raise SAFIException(f'API do SAFI não retornou termos de contrato.')
        else:
            raise SAFIException(f'API SAFI com erro. Status: {response.status_code}')

    @classmethod
    def get_contrato(cls, contrato_uuid):
        """Retorna informaçãoes de contrato."""
        response = requests.get(f'{DJANGO_SAFI_API_URL}/contratos-sigpae/{contrato_uuid}/',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            resultado = response.json()
            if resultado:
                return resultado
            raise SAFIException(f'API do SAFI não retornou nada para o contrato: {contrato_uuid}')
        else:
            raise SAFIException(f'API SAFI com erro. Status: {response.status_code}')
