from rest_framework import serializers

from sme_pratoaberto_terceirizadas.escola.models import Lote
from ...models import (Terceirizada, Nutricionista)


class NutricionistaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutricionista
        exclude = ('id', 'terceirizada')


class TerceirizadaCreateSerializer(serializers.ModelSerializer):
    lotes = serializers.SlugRelatedField(slug_field='uuid', many=True, queryset=Lote.objects.all())
    nutricionistas = NutricionistaCreateSerializer(many=True)

    def create(self, validated_data):
        nutricionistas_array = validated_data.pop('nutricionistas')
        lotes = validated_data.pop('lotes', [])
        terceirizada = Terceirizada.objects.create(**validated_data)
        terceirizada.lotes.set(lotes)
        for nutri_json in nutricionistas_array:
            nutricionista = NutricionistaCreateSerializer().create(nutri_json)
            nutricionista.terceirizada = terceirizada
            nutricionista.save()
        return terceirizada

    class Meta:
        model = Terceirizada
        exclude = ('id',)
