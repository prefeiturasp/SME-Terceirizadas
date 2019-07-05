import datetime

from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.utils import obter_dias_uteis_apos, eh_dia_util


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


def solicitacao_deve_ter_1_ou_mais_kits(lista_igual: bool, numero_kits: int):
    deve_ter_1_ou_mais_kit = lista_igual is True and numero_kits >= 1
    if not deve_ter_1_ou_mais_kit:
        raise serializers.ValidationError(
            'Quando lista_kit_lanche_igual é Verdadeiro, '
            '"dado_base", deve ter de 1 a 3 kits')


def solicitacao_deve_ter_0_kit(lista_igual: bool, numero_kits: int):
    deve_ter_nenhum_kit = lista_igual is False and numero_kits == 0
    if not deve_ter_nenhum_kit:
        raise serializers.ValidationError(
            'Quando lista_kit_lanche_igual é Falso, '
            '"dado_base", deve ter 0 kits, cada escola deve ter uma '
            'especificação própria dos seus kit-lanches.')


def escola_quantidade_deve_ter_0_kit(numero_kits: int, indice: int,):
    deve_ter_nenhum_kit = numero_kits == 0
    if not deve_ter_nenhum_kit:
        raise serializers.ValidationError(
            'escola_quantidade indice #{} deve ter 0 kit'
            ' pois a lista é igual para todas as escolas'.format(indice)
        )


def escola_quantidade_deve_ter_mesmo_tempo_passeio(escola_quantidade,
                                                   dado_base,
                                                   indice):
    tempo_passeio_escola = escola_quantidade.get('tempo_passeio')
    tempo_passeio_geral = dado_base.get('tempo_passeio')

    if tempo_passeio_escola != tempo_passeio_geral:
        raise serializers.ValidationError(
            'escola_quantidade indice #{} deve diverge do tempo'
            ' de dado_base, esperado: {}, recebido: {}'.format(
                indice, tempo_passeio_geral, tempo_passeio_escola)
        )


def valida_tempo_passeio_lista_igual(lista_igual: bool, tempo_passeio):
    if lista_igual is not True:
        return
    tentativa1 = lista_igual and type(tempo_passeio) == int

    if not tentativa1:
        raise serializers.ValidationError(
            'Quando o lista_kit_lanche_igual for Verdadeiro, tempo de passeio deve '
            'ser de 0 a 2.')


def valida_tempo_passeio_lista_nao_igual(lista_igual: bool, tempo_passeio):
    if lista_igual is not False:
        return
    tentativa2 = not lista_igual and tempo_passeio is None

    if not tentativa2:
        raise serializers.ValidationError(
            'Quando o lista_kit_lanche_igual for Falso, tempo de passeio deve '
            'ser null. Cada escola deve ter uma '
            'especificação própria dos seus kit-lanches.')
