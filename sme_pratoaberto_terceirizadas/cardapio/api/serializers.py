from rest_framework import serializers

from sme_pratoaberto_terceirizadas.escola.models import Escola
from sme_pratoaberto_terceirizadas.dados_comuns.validators import (nao_pode_ser_passado,
                                                                   deve_pedir_com_antecedencia,
                                                                   dia_util, verificar_se_existe)
from ..models import AlteracaoCardapio


class EscolaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escola
        fields = '__all__'


class AlteracaoCardapioSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(slug_field='uuid', queryset=Escola.objects.all())

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

    def _validate_ja_cadastrado(self, data):
        inicio = data.get('data_inicial', None)
        fim = data.get('data_final', None)
        escola = data.get('escola', None)
        existe = verificar_se_existe(AlteracaoCardapio,
                                     data_inicial=inicio,
                                     data_final=fim,
                                     escola=escola)
        if existe:
            raise serializers.ValidationError('Solicitação já foi cadastrada')
        return data

    def validate(self, data):
        self._validate_ja_cadastrado(data)
        data_inicial = data.get('data_inicial', None)
        data_final = data.get('data_final', None)
        if data_inicial and data_final:
            if data_inicial > data_final:
                raise serializers.ValidationError('Data inicial não deve ser maior que a data final')
        return data
