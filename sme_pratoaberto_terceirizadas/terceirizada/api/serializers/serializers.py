from rest_framework import serializers

from ...models import (Edital, Terceirizada, Nutricionista)
from sme_pratoaberto_terceirizadas.dados_comuns.api.serializers import ContatoSerializer


class EditalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        exclude = ('id',)


class NutricionistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutricionista
        exclude = ('id', 'terceirizada')


class TerceirizadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terceirizada
        exclude = ('id',)


class TerceirizadaSimplesSerializer(serializers.ModelSerializer):
    contato = ContatoSerializer()

    class Meta:
        model = Terceirizada
        fields = ('uuid', 'cnpj', 'nome_fantasia', 'contato')
