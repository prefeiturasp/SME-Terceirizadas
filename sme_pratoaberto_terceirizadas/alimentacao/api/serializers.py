from rest_framework import serializers

from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio, InverterDiaCardapio
from sme_pratoaberto_terceirizadas.school.api.serializers import SchoolSerializer


class CardapioSerializer(serializers.ModelSerializer):
    escolas = SchoolSerializer(many=True, read_only=True)

    class Meta:
        model = Cardapio
        fields = '__all__'


class InverterDiaCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = InverterDiaCardapio
        fields = '__all__'
