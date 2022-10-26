from datetime import date

from sme_terceirizadas.pre_recebimento.models import Cronograma


def gera_proximo_numero_cronograma():
    ano = date.today().year
    ultimo_cronograma = Cronograma.objects.last()
    if ultimo_cronograma:
        return f'{str(int(ultimo_cronograma.numero[:3]) + 1).zfill(3)}/{ano}'
    else:
        return f'001/{ano}'
