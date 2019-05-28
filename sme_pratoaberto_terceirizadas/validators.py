import datetime

from rest_framework import serializers

from sme_pratoaberto_terceirizadas.common_data.utils import get_working_days_after, is_working_day


def nao_pode_ser_passado(data: datetime.date):
    if data < datetime.date.today():
        raise serializers.ValidationError('Não pode ser no passado')
    return True


def deve_pedir_com_antecedencia(data: datetime.date, dias: int = 2):
    prox_dia_util = get_working_days_after(dias)
    if data <= prox_dia_util:
        raise serializers.ValidationError('Deve pedir com pelo menos {} dias úteis de antecedência'.format(dias))
    return True


def dia_util(data: datetime.date):
    if not is_working_day(data):
        raise serializers.ValidationError('Não é dia útil em São Paulo')
    return True


# TODO: validar o primeiro parametro pra ser instance of Model
def verificar_se_existe(obj_model, **kwargs) -> bool:
    qtd = obj_model.objects.filter(**kwargs).count()
    if qtd:
        return True
    return False
