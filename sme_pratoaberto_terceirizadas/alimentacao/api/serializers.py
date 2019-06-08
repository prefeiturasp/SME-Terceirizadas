from rest_framework import serializers

from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio


class CardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cardapio
        fields = '__all__'
