from rest_framework import serializers

from sme_pratoaberto_terceirizadas.school.models import School
from sme_pratoaberto_terceirizadas.validators import (nao_pode_ser_passado,
                                                      deve_pedir_com_antecedencia,
                                                      dia_util)
from ..models import AlteracaoCardapio


class EscolaSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class AlteracaoCardapioSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(slug_field='uuid', queryset=School.objects.all())

    class Meta:
        model = AlteracaoCardapio
        fields = '__all__'

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

    def validate_ja_cadastrado(self, data):
        if not AlteracaoCardapio.valida_existencia(data):
            raise serializers.ValidationError('Solicitação já foi cadastrada')
        return data

    def validate(self, data):
        self.validate_ja_cadastrado(data)
        data_inicial = data.get('data_inicial', None)
        data_final = data.get('data_final', None)
        if data_inicial and data_final:
            if data_inicial > data_final:
                raise serializers.ValidationError('Data inicial não deve ser maior que a data final')
        return data
