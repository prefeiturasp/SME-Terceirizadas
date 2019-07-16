from rest_framework import serializers

from ..helpers import notificar_partes_interessadas
from sme_pratoaberto_terceirizadas.cardapio.api.validators import cardapio_antigo, valida_duplicidade, \
    valida_cardapio_de_para
from sme_pratoaberto_terceirizadas.cardapio.models import InversaoCardapio, Cardapio
from sme_pratoaberto_terceirizadas.escola.models import Escola


class InversaoCardapioSerializerCreate(serializers.ModelSerializer):
    cardapio_de = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Cardapio.objects.all()
    )

    cardapio_para = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Cardapio.objects.all()
    )

    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )

    def validate_cardapio_de(self, attr):
        cardapio_antigo(attr)
        return attr

    def validate_cardapio_para(self, attr):
        cardapio_antigo(attr)
        return attr

    def validate(self, attrs):
        valida_cardapio_de_para(attrs.get('cardapio_de'), attrs.get('cardapio_para'))
        valida_duplicidade(attrs.get('cardapio_de'), attrs.get('cardapio_para'), attrs.get('escola'))
        return attrs

    def create(self, validated_data):
        inversao_cardapio = InversaoCardapio.objects.create(**validated_data)
        if inversao_cardapio.pk:
            usuario = self.context['user']
            notificar_partes_interessadas(usuario, **validated_data)
        return inversao_cardapio

    class Meta:
        model = InversaoCardapio
        fields = ['uuid', 'descricao', 'cardapio_de', 'cardapio_para', 'escola']
