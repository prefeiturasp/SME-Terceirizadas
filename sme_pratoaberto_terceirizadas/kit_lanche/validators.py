from rest_framework import serializers

from sme_pratoaberto_terceirizadas.kit_lanche.models import EscolaQuantidade


def deve_ter_1_kit_somente(lista_igual, numero_kits):
    deve_ter_1_kit = lista_igual is True and numero_kits == 1
    if not deve_ter_1_kit:
        raise serializers.ValidationError('Em "dado_base", quando lista_kit_lanche é igual, deve ter somente 1 kit')


def solicitacao_deve_ter_1_ou_mais_kits(numero_kits: int):
    deve_ter_1_ou_mais_kit = numero_kits >= 1
    if not deve_ter_1_ou_mais_kit:
        raise serializers.ValidationError(
            'Quando lista_kit_lanche_igual é Verdadeiro, '
            '"dado_base", deve ter de 1 a 3 kits')
    return True


def solicitacao_deve_ter_0_kit(numero_kits: int):
    deve_ter_nenhum_kit = numero_kits == 0
    if not deve_ter_nenhum_kit:
        raise serializers.ValidationError('Em "dado_base", quando lista_kit_lanche NÃO é igual, deve ter 0 kit')
    return True


def escola_quantidade_deve_ter_0_kit(numero_kits: int, indice: int, ):
    deve_ter_nenhum_kit = numero_kits == 0
    if not deve_ter_nenhum_kit:
        raise serializers.ValidationError(
            'escola_quantidade indice # {} deve ter 0 kit'
            ' pois a lista é igual para todas as escolas'.format(indice)
        )
    return True


def escola_quantidade_deve_ter_1_ou_mais_kits(numero_kits: int, indice: int, ):
    deve_ter_um_ou_mais = numero_kits >= 1
    if not deve_ter_um_ou_mais:
        raise serializers.ValidationError(
            'escola_quantidade indice # {} deve ter 1 ou mais kits'.format(indice)
        )
    return True


def escola_quantidade_deve_ter_mesmo_tempo_passeio(escola_quantidade,
                                                   dado_base,
                                                   indice):
    tempo_passeio_escola = escola_quantidade.get('tempo_passeio')
    tempo_passeio_geral = dado_base.get('tempo_passeio')

    if tempo_passeio_escola != tempo_passeio_geral:
        raise serializers.ValidationError(
            'escola_quantidade indice #{} diverge do tempo_passeio'
            ' de dado_base. Esperado: {}, recebido: {}'.format(
                indice, tempo_passeio_geral, tempo_passeio_escola)
        )
    return True


def valida_tempo_passeio_lista_igual(tempo_passeio):
    horas = [h[0] for h in EscolaQuantidade.HORAS]
    tentativa1 = tempo_passeio in horas
    if not tentativa1:
        raise serializers.ValidationError(
            'Quando o lista_kit_lanche_igual for Verdadeiro, tempo de passeio deve '
            'ser qualquer uma das opções: {}.'.format(horas))
    return True


def valida_tempo_passeio_lista_nao_igual(tempo_passeio):
    tentativa2 = tempo_passeio is None

    if not tentativa2:
        raise serializers.ValidationError(
            'Quando o lista_kit_lanche_igual for Falso, tempo de passeio deve '
            'ser null. Cada escola deve ter uma '
            'especificação própria dos seus kit-lanches.')
    return True
