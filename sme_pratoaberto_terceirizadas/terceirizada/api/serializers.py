from rest_framework import serializers

from ..models import (Lote, Edital)


class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        exclude = ('id', 'diretoria_regional')


class EditalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        exclude = ('id',)
