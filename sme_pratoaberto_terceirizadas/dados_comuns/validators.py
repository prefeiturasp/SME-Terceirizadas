import datetime

from rest_framework import serializers
from workalendar.america import BrazilSaoPauloCity

from ..dados_comuns.utils import obter_dias_uteis_apos, eh_dia_util

calendario = BrazilSaoPauloCity()


def nao_pode_ser_passado(data: datetime.date):
    if data < datetime.date.today():
        raise serializers.ValidationError('Não pode ser no passado')
    return True


def deve_pedir_com_antecedencia(dia: datetime.date, dias: int = 2):
    prox_dia_util = obter_dias_uteis_apos(days=dias, date=datetime.datetime.today())
    if dia <= prox_dia_util:
        raise serializers.ValidationError('Deve pedir com pelo menos {} dias úteis de antecedência'.format(dias))
    return True


def dia_util(data: datetime.date):
    if not eh_dia_util(data):
        raise serializers.ValidationError('Não é dia útil em São Paulo')
    return True


# TODO: validar o primeiro parametro pra ser instance of Model
def verificar_se_existe(obj_model, **kwargs) -> bool:
    qtd = obj_model.objects.filter(**kwargs).count()
    if qtd:
        return True
    return False


def objeto_nao_deve_ter_duplicidade(obj_model, mensagem="Objeto já existe", **kwargs, ):
    qtd = obj_model.objects.filter(**kwargs).count()
    if qtd:
        raise serializers.ValidationError(mensagem)


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


def solicitacao_deve_ter_0_kit(numero_kits: int):
    deve_ter_nenhum_kit = numero_kits == 0
    if not deve_ter_nenhum_kit:
        raise serializers.ValidationError('Em "dado_base", quando lista_kit_lanche NÃO é igual, deve ter 0 kit')


def nao_pode_ser_feriado(data: datetime.date, mensagem='Não pode ser no feriado'):
    if calendario.is_holiday(data):
        raise serializers.ValidationError(mensagem)


def escola_quantidade_deve_ter_0_kit(numero_kits: int, indice: int, ):
    deve_ter_nenhum_kit = numero_kits == 0
    if not deve_ter_nenhum_kit:
        raise serializers.ValidationError(
            'escola_quantidade indice # {} deve ter 0 kit'
            ' pois a lista é igual para todas as escolas'.format(indice)
        )


def escola_quantidade_deve_ter_1_ou_mais_kits(numero_kits: int, indice: int, ):
    deve_ter_um_ou_mais = numero_kits >= 1
    if not deve_ter_um_ou_mais:
        raise serializers.ValidationError(
            'escola_quantidade indice # {} deve ter 1 ou mais kits'.format(indice)
        )


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


def valida_tempo_passeio_lista_igual(tempo_passeio):
    tentativa1 = type(tempo_passeio) == int

    if not tentativa1:
        raise serializers.ValidationError(
            'Quando o lista_kit_lanche_igual for Verdadeiro, tempo de passeio deve '
            'ser de 0 a 2.')


def valida_tempo_passeio_lista_nao_igual(tempo_passeio):
    tentativa2 = tempo_passeio is None

    if not tentativa2:
        raise serializers.ValidationError(
            'Quando o lista_kit_lanche_igual for Falso, tempo de passeio deve '
            'ser null. Cada escola deve ter uma '
            'especificação própria dos seus kit-lanches.')
