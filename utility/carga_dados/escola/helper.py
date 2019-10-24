import json
from unicodedata import normalize
from django.conf import settings
import datetime
from sme_terceirizadas.perfil.models import Vinculo


def normaliza_nome(nome):
    nome = nome.replace(' / ', '/')
    nome = normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return nome


def somente_digitos(palavra):
    return ''.join(p for p in palavra if p in '0123456789')


def coloca_zero_a_esquerda(palavra, tam=6):
    tam_palavra = len(palavra)
    qtd_zeros = tam - tam_palavra
    zeros = '0' * qtd_zeros
    final = ''
    if tam_palavra < tam:
        final = zeros + palavra
    return final or palavra


def busca_sigla_lote(sigla):
    # Santo Amaro > Não tem escola associada a esse lote OBS: "SAM" eh nao existe
    # Pirituba > Não tem escola associada a esse lote OBS: "PIR" eh nao existe
    # Butanta > Não tem escola associada a esse lote OBS: "BTT" eh nao existe

    fixture_data = json.load(
        open('{0}/sme_terceirizadas/escola/fixtures/lotes.json'.format(settings.ROOT_DIR))
    )

    def _get_id(data):
        try:
            return list(
                filter(lambda item: item["fields"]["iniciais"] == data, fixture_data)
            )[0]["id"]
        except (IndexError, TypeError) as ex:
            raise Exception("Siga do Lote Nao Encontrado, %s" % str(ex)) from None

    if sigla.strip() == 'MP':
        return _get_id('MP I')
    else:
        return _get_id(sigla.strip())


def cria_vinculo_de_perfil_usuario(perfil, usuario, instituicao):
    vinculo = Vinculo.objects.create(
        data_inicial=datetime.date.today(),
        instituicao=instituicao,
        perfil=perfil,
        usuario=usuario
    )
    return vinculo
