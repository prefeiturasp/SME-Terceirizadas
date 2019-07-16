from rest_framework import serializers

from sme_pratoaberto_terceirizadas.cardapio.api.validators import cardapio_antigo, valida_duplicidade, \
    valida_cardapio_de_para
from sme_pratoaberto_terceirizadas.cardapio.models import InversaoCardapio, Cardapio, TipoAlimentacao
from sme_pratoaberto_terceirizadas.dados_comuns.validators import nao_pode_ser_passado, nao_pode_ser_feriado, \
    objeto_nao_deve_ter_duplicidade
from sme_pratoaberto_terceirizadas.escola.models import Escola
from sme_pratoaberto_terceirizadas.terceirizada.models import Edital


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
        # TODO criar as notificações e disparar e-mails
        return inversao_cardapio

    class Meta:
        model = InversaoCardapio
        fields = ['uuid', 'descricao', 'cardapio_de', 'cardapio_para', 'escola']


class CardapioCreateSerializer(serializers.ModelSerializer):
    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        required=True,
        queryset=TipoAlimentacao.objects.all()
    )
    edital = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Edital.objects.all()
    )

    def validate_data(self, data):
        nao_pode_ser_passado(data)
        nao_pode_ser_feriado(data)
        objeto_nao_deve_ter_duplicidade(
            Cardapio,
            mensagem='Já existe um cardápio cadastrado com esta data',
            data=data
        )
        return data

    class Meta:
        model = Cardapio
        exclude = ('id',)
