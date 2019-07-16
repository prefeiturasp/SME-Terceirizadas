from rest_framework import serializers

from sme_pratoaberto_terceirizadas.cardapio.api.validators import cardapio_antigo, valida_duplicidade, \
    valida_cardapio_de_para
from sme_pratoaberto_terceirizadas.cardapio.models import InversaoCardapio, Cardapio, TipoAlimentacao, \
    SuspensaoAlimentacao
from sme_pratoaberto_terceirizadas.dados_comuns.validators import nao_pode_ser_passado, nao_pode_ser_feriado, \
    objeto_nao_deve_ter_duplicidade
from sme_pratoaberto_terceirizadas.escola.models import Escola, PeriodoEscolar
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


class SuspensaoAlimentacaoCreateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    cardapio = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Cardapio.objects.all()
    )
    periodos = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        required=False,
        queryset=PeriodoEscolar.objects.all()
    )
    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        required=False,
        queryset=TipoAlimentacao.objects.all()
    )

    def validate_data(self, data):
        nao_pode_ser_passado(data)
        return data

    def create(self, validated_data):
        periodos = validated_data.pop('periodos', [])
        tipos_alimentacao = validated_data.pop('tipos_alimentacao', [])

        suspensao_alimentacao = SuspensaoAlimentacao.objects.create(
            **validated_data
        )
        suspensao_alimentacao.periodos.set(periodos)
        suspensao_alimentacao.tipos_alimentacao.set(tipos_alimentacao)

        return suspensao_alimentacao

    def validate(self, attrs):
        tipo = attrs.get('tipo')
        cardapio = attrs.get('cardapio')
        periodos = attrs.get('periodos', [])
        tipos_alimentacao = attrs.get('tipos_alimentacao', [])
        if tipo == SuspensaoAlimentacao.CARDAPIO_INTEIRO:
            if not cardapio:
                raise serializers.ValidationError(
                    f'Quando tipo {tipo} (cardápio inteiro), deve ter cardápio')
            if periodos or tipos_alimentacao:
                raise serializers.ValidationError(
                    f'Quando tipo {tipo} (cardápio inteiro), não pode ter períodos ou tipos de alimentação')
        elif tipo == SuspensaoAlimentacao.PERIODO_ESCOLAR:
            if not periodos:
                raise serializers.ValidationError(
                    f'Quando tipo {tipo} (periodo escolar), deve ter ao menos 1 periodo escolar')
            if cardapio or tipos_alimentacao:
                raise serializers.ValidationError(
                    f'Quando tipo {tipo} (periodo escolar), não pode ter cardapio ou tipos de alimentação')
        elif tipo == SuspensaoAlimentacao.TIPO_ALIMENTACAO:
            if not tipos_alimentacao:
                raise serializers.ValidationError(
                    f'Quando tipo {tipo} (tipo alimentação), deve ter ao menos 1 tipo de alimentação')
            if cardapio or periodos:
                raise serializers.ValidationError(
                    f'Quando tipo {tipo} (tipo alimentação), não pode ter cardapio ou períodos')
        return attrs

    class Meta:
        model = SuspensaoAlimentacao
        exclude = ('id',)
