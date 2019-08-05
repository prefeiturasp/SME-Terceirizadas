from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_pratoaberto_terceirizadas.dados_comuns.validators import (
    nao_pode_ser_no_passado, nao_pode_ser_feriado,
    objeto_nao_deve_ter_duplicidade
)
from sme_pratoaberto_terceirizadas.escola.models import Escola, PeriodoEscolar
from sme_pratoaberto_terceirizadas.terceirizada.models import Edital
from ..helpers import notificar_partes_envolvidas
from sme_pratoaberto_terceirizadas.dados_comuns.validators import deve_existir_cardapio
from ...models import (
    InversaoCardapio, Cardapio,
    TipoAlimentacao, SuspensaoAlimentacao,
    AlteracaoCardapio, MotivoAlteracaoCardapio, SubstituicoesAlimentacaoNoPeriodoEscolar,
    SuspensaoAlimentacaoNoPeriodoEscolar, MotivoSuspensao)


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
        deve_existir_cardapio(attrs['escola'], attrs['data_de'])
        return attrs

    def create(self, validated_data):
        data_de = validated_data.pop('data_de')
        data_para = validated_data.pop('data_para')
        escola = validated_data.get('escola')
        validated_data['cardapio_de'] = escola.get_cardapio(data_de)
        validated_data['cardapio_para'] = escola.get_cardapio(data_para)
        validated_data['criado_por'] = self.context['request'].user

        inversao_cardapio = InversaoCardapio.objects.create(**validated_data)
        if inversao_cardapio.pk:
            usuario = self.context.get('request').user
            notificar_partes_envolvidas(usuario, **validated_data)
        return inversao_cardapio

    def update(self, instance, validated_data):
        data_de = validated_data.pop('data_de')
        data_para = validated_data.pop('data_para')
        escola = validated_data.get('escola')
        validated_data['cardapio_de'] = escola.get_cardapio(data_de)
        validated_data['cardapio_para'] = escola.get_cardapio(data_para)
        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = InversaoCardapio
        fields = ('uuid', 'descricao', 'data_de', 'data_para', 'escola')


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


class SuspensaoAlimentacaoNoPeriodoEscolarCreateSerializer(serializers.ModelSerializer):
    periodo_escolar = serializers.SlugRelatedField(slug_field='uuid',
                                                   queryset=PeriodoEscolar.objects.all())
    tipos_alimentacao = serializers.SlugRelatedField(slug_field='uuid',
                                                     many=True,
                                                     queryset=TipoAlimentacao.objects.all())

    class Meta:
        model = SuspensaoAlimentacaoNoPeriodoEscolar
        exclude = ('id', 'suspensao_alimentacao')


class SuspensaoAlimentacaoCreateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=MotivoSuspensao.objects.all()
    )
    suspensoes_periodo_escolar = SuspensaoAlimentacaoNoPeriodoEscolarCreateSerializer(many=True)

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        return data

    def create(self, validated_data):
        suspensoes_periodo_escolar_json = validated_data.pop('suspensoes_periodo_escolar', [])

        suspensao_alimentacao = SuspensaoAlimentacao.objects.create(
            **validated_data
        )
        suspensao_alimentacao.suspensoes_periodo_escolar.set(suspensoes_periodo_escolar_json)

        return suspensao_alimentacao

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
