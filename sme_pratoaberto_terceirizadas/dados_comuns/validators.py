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


def deve_ter_1_kit_somente(lista_igual, numero_kits):
    deve_ter_1_kit = lista_igual is True and numero_kits == 1
    if not deve_ter_1_kit:
        raise serializers.ValidationError('Em "dado_base", quando lista_kit_lanche é igual, deve ter somente 1 kit')


def deve_ter_0_kit(lista_igual, numero_kits):
    deve_ter_nenhum_kit = lista_igual is False and numero_kits == 0
    if not deve_ter_nenhum_kit:
        raise serializers.ValidationError('Em "dado_base", quando lista_kit_lanche NÃO é igual, deve ter 0 kit')
