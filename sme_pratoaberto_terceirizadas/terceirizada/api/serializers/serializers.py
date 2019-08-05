from rest_framework import serializers

from ...models import (Edital, Terceirizada, Nutricionista)


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
