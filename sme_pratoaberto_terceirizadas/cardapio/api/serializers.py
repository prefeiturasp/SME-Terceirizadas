import datetime

from rest_framework import serializers

from sme_pratoaberto_terceirizadas.common_data.utils import get_working_days_after, is_working_day
from ..models import AlteracaoCardapio


def dentro_do_intervalo(validate_date, trial_date):
    if trial_date > validate_date:
        raise serializers.ValidationError('ERRO {} {}'.format(validate_date, trial_date))


def nao_pode_ser_passado(validate_date):
    if validate_date < datetime.date.today():
        raise serializers.ValidationError('Não pode ser no passado')


def deve_pedir_com_antecedencia(validate_date, dias=2):
    next_2_working_days = get_working_days_after(dias)
    if validate_date <= next_2_working_days:
        raise serializers.ValidationError('Deve pedir com pelo menos {} dias úteis de antecedência'.format(dias))


def dia_util(validate_date):
    if not is_working_day(validate_date):
        raise serializers.ValidationError('Não é dia útil em São Paulo')


class AlteracaoCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlteracaoCardapio
        fields = ('uuid', 'name', 'description', 'data_inicial', 'data_final')

    # https://www.django-rest-framework.org/api-guide/serializers/#field-level-validation

    def validate_data_inicial(self, data_inicial):
        nao_pode_ser_passado(data_inicial)
        deve_pedir_com_antecedencia(data_inicial)
        dia_util(data_inicial)
        return data_inicial

    def validate_data_final(self, data_final):
        nao_pode_ser_passado(data_final)
        dia_util(data_final)
        return data_final

    def validate(self, data):
        data_inicial = data.get('data_inicial')
        data_final = data.get('data_final')

        if data_inicial > data_final:
            raise serializers.ValidationError("Data inicial não deve ser maior que a data final ")
        return data
