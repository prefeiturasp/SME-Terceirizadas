import requests
from rest_framework import status

from ..dados_comuns.constants import DJANGO_NOVO_SGP_API_TOKEN, DJANGO_NOVO_SGP_API_URL


class NovoSGPServico:
    HEADER = {
        'x-sgp-api-key': f'{DJANGO_NOVO_SGP_API_TOKEN}'
    }
    TIMEOUT = 10

    @classmethod
    def dias_letivos(cls, codigo_eol: str, data_inicio: str, data_fim: str, tipo_turno: int = 1):
        """Consulta a quantidade de matriculados na API do sgp."""

        response = requests.get(f'{DJANGO_NOVO_SGP_API_URL}/v1/calendario/integracoes/ues/dias-letivos/',
                                headers=cls.HEADER, timeout=cls.TIMEOUT,
                                params={'UeCodigo': codigo_eol, 'TipoTurno': tipo_turno,
                                        'DataInicio': data_inicio, 'DataFim': data_fim})

        if response.status_code == status.HTTP_200_OK:
            resultado = response.json()
            return resultado
        else:
            raise Exception(f'API EOL do SGP está com erro. Erro: {str(response)}, Status: {response.status_code}')
