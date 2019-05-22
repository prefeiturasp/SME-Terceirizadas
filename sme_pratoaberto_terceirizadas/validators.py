import datetime

from rest_framework import serializers

from sme_pratoaberto_terceirizadas.common_data.utils import get_working_days_after, is_working_day


def nao_pode_ser_passado(data: datetime.date):
    if data < datetime.date.today():
        raise serializers.ValidationError('Não pode ser no passado')


def deve_pedir_com_antecedencia(data: datetime.date, dias: int = 2):
    prox_dia_util = get_working_days_after(dias)
    if data <= prox_dia_util:
        raise serializers.ValidationError('Deve pedir com pelo menos {} dias úteis de antecedência'.format(dias))


def dia_util(data: datetime.date):
    if not is_working_day(data):
        raise serializers.ValidationError('Não é dia útil em São Paulo')
