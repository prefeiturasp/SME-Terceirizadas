from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.utils import update_instance_from_dict, enviar_notificacao
from sme_pratoaberto_terceirizadas.dados_comuns.validators import (
    nao_pode_ser_no_passado, nao_pode_ser_feriado,
    objeto_nao_deve_ter_duplicidade, existe_cardapio
)
from sme_pratoaberto_terceirizadas.escola.models import Escola, PeriodoEscolar
from sme_pratoaberto_terceirizadas.perfil.models import Usuario
from sme_pratoaberto_terceirizadas.terceirizada.models import Edital
from ..helpers import notificar_partes_envolvidas
from ...api.validators import (
    valida_tipo_cardapio_inteiro,
    valida_tipo_periodo_escolar, valida_tipo_alimentacao,
)
from ...models import (
    InversaoCardapio, Cardapio,
    TipoAlimentacao, SuspensaoAlimentacao,
    AlteracaoCardapio, MotivoAlteracaoCardapio, SubstituicoesAlimentacaoNoPeriodoEscolar)


class InversaoCardapioSerializerCreate(serializers.ModelSerializer):
    data_de = serializers.DateField()
    data_para = serializers.DateField()

    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )

    def validate_data_de(self, data_de):
        nao_pode_ser_no_passado(data_de)
        return data_de

    def validate_data_para(self, data_para):
        nao_pode_ser_no_passado(data_para)
        return data_para

    def validate(self, attrs):
        existe_cardapio(attrs['escola'], attrs['data_de'])
        existe_cardapio(attrs['escola'], attrs['data_para'])
        return attrs

    def create(self, validated_data):
        data_de = validated_data.pop('data_de')
        data_para = validated_data.pop('data_para')
        escola = validated_data.get('escola')
        validated_data['cardapio_de'] = escola.get_cardapio(data_de)
        validated_data['cardapio_para'] = escola.get_cardapio(data_para)
        inversao_cardapio = InversaoCardapio.objects.create(**validated_data)
        if inversao_cardapio.pk:
            usuario = self.context.get('request').user
            notificar_partes_envolvidas(usuario, **validated_data)
        return inversao_cardapio

    class Meta:
        model = InversaoCardapio
        fields = ('uuid', 'descricao', 'observacao', 'data_de', 'data_para', 'escola')


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
        nao_pode_ser_no_passado(data)
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
    criado_por = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Usuario.objects.all()
    )
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
    periodos_escolares = serializers.SlugRelatedField(
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
    tipo_explicacao = serializers.CharField(
        source='get_tipo_display',
        required=False,
        read_only=True)

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        return data

    def create(self, validated_data):
        periodos_escolares = validated_data.pop('periodos_escolares', [])
        tipos_alimentacao = validated_data.pop('tipos_alimentacao', [])

        suspensao_alimentacao = SuspensaoAlimentacao.objects.create(
            **validated_data
        )
        suspensao_alimentacao.periodos_escolares.set(periodos_escolares)
        suspensao_alimentacao.tipos_alimentacao.set(tipos_alimentacao)
        enviar_notificacao(sender=suspensao_alimentacao.criado_por,
                           recipients=suspensao_alimentacao.notificacao_enviar_para,
                           short_desc="Criação de Suspensão de Alimentação",
                           long_desc=("Uma Suspensão de Alimentação foi criada por " +
                                      suspensao_alimentacao.criado_por.nome))

        return suspensao_alimentacao

    def validate(self, attrs):
        tipo = attrs.get('tipo')
        cardapio = attrs.get('cardapio')
        periodos_escolares = attrs.get('periodos_escolares', [])
        tipos_alimentacao = attrs.get('tipos_alimentacao', [])
        if tipo == SuspensaoAlimentacao.CARDAPIO_INTEIRO:
            valida_tipo_cardapio_inteiro(cardapio, periodos_escolares, tipo, tipos_alimentacao)
        elif tipo == SuspensaoAlimentacao.PERIODO_ESCOLAR:
            valida_tipo_periodo_escolar(cardapio, periodos_escolares, tipo, tipos_alimentacao)
        elif tipo == SuspensaoAlimentacao.TIPO_ALIMENTACAO:
            valida_tipo_alimentacao(cardapio, periodos_escolares, tipo, tipos_alimentacao)
        return attrs

    class Meta:
        model = SuspensaoAlimentacao
        exclude = ('id',)


class SubstituicoesAlimentacaoNoPeriodoEscolarSerializerCreate(serializers.ModelSerializer):
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=PeriodoEscolar.objects.all()
    )
    alteracao_cardapio = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AlteracaoCardapio.objects.all()
    )

    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=TipoAlimentacao.objects.all(),
        many=True
    )

    def create(self, validated_data):
        tipos_alimentacao = validated_data.pop('tipos_alimentacao')

        substituicoes_alimentacao = SubstituicoesAlimentacaoNoPeriodoEscolar.objects.create(**validated_data)
        substituicoes_alimentacao.tipos_alimentacao.set(tipos_alimentacao)

        return substituicoes_alimentacao

    def update(self, instance, validated_data):
        tipos_alimentacao = validated_data.pop('tipos_alimentacao')
        update_instance_from_dict(instance, validated_data)
        instance.tipos_alimentacao.set(tipos_alimentacao)
        instance.save()
        return instance

    class Meta:
        model = SubstituicoesAlimentacaoNoPeriodoEscolar
        exclude = ('id',)


class AlteracaoCardapioSerializerCreate(serializers.ModelSerializer):
    """
    Exemplo de um payload de criação de Alteração de Cardápio
    {
      "escola": "c0cc9d5e-563a-48e4-bf53-22d47b6347b4",

      "motivo": "3f1684f9-0dd9-4cce-9c56-f07164f857b9",

      "data_inicial": "01/01/2018",
      "data_final": "26/07/2019",
      "observacao": "Teste",

      "substituicoes": [
        {
          "periodo_escolar": "811ab9bd-a25a-4304-9ae4-a48a3eaae24b",
          "tipos_alimentacao": ["5aca23f2-055d-4f73-9bf5-6ed39dbd8407"],
          "qtd_alunos": 100
        },
        {
          "periodo_escolar": "30782fd8-4db6-4947-995a-0e9f85e1d9bf",
          "tipos_alimentacao": ["5aca23f2-055d-4f73-9bf5-6ed39dbd8407", "7c0af352-5439-47a5-a945-7f882e89a4b3"],
          "qtd_alunos": 100
        }
      ]

    }
    """

    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=MotivoAlteracaoCardapio.objects.all()
    )

    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )

    substituicoes = SubstituicoesAlimentacaoNoPeriodoEscolarSerializerCreate(many=True)

    def create(self, validated_data):
        substituicoes = validated_data.pop('substituicoes')

        substituicoes_lista = []
        for substituicao in substituicoes:
            substituicoes_object = SubstituicoesAlimentacaoNoPeriodoEscolarSerializerCreate(
            ).create(substituicao)
            substituicoes_lista.append(substituicoes_object)
        alteracao_cardapio = AlteracaoCardapio.objects.create(**validated_data)
        alteracao_cardapio.substituicoes.set(substituicoes_lista)

        usuario = self.context.get('request').user
        notificar_partes_envolvidas(usuario, **validated_data)
        return alteracao_cardapio

    def update(self, instance, validated_data):
        substituicoes_array = validated_data.pop('substituicoes')
        substituicoes_obj = instance.substituicoes.all()

        for index in range(len(substituicoes_array)):
            SubstituicoesAlimentacaoNoPeriodoEscolarSerializerCreate(
            ).update(instance=substituicoes_obj[index],
                     validated_data=substituicoes_array[index])

        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = AlteracaoCardapio
        exclude = ('id',)
