from rest_framework import serializers

from ..models import AlteracaoCardapio


class AlteracaoCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlteracaoCardapio
        fields = ('name', 'data_inicial', 'data_final')
