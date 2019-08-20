from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_pratoaberto_terceirizadas.dados_comuns.validators import deve_existir_cardapio, deve_pedir_com_antecedencia
from sme_pratoaberto_terceirizadas.dados_comuns.validators import (
    nao_pode_ser_no_passado, nao_pode_ser_feriado,
    objeto_nao_deve_ter_duplicidade
)
from sme_pratoaberto_terceirizadas.escola.models import Escola, PeriodoEscolar
from sme_pratoaberto_terceirizadas.terceirizada.models import Edital
from ..helpers import notificar_partes_envolvidas
from ...api.validators import (
    valida_duplicidade, valida_cardapio_de_para
)
from ...models import (
    InversaoCardapio, Cardapio,
    TipoAlimentacao, SuspensaoAlimentacao,
    AlteracaoCardapio, MotivoAlteracaoCardapio, SubstituicoesAlimentacaoNoPeriodoEscolar,
    SuspensaoAlimentacaoNoPeriodoEscolar, MotivoSuspensao, GrupoSuspensaoAlimentacao,
    QuantidadePorPeriodoSuspensaoAlimentacao)


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
        valida_cardapio_de_para(attrs.get('data_de'), attrs.get('data_para'))
        valida_duplicidade(attrs.get('data_de'), attrs.get('data_para'), attrs.get('escola'))
        deve_existir_cardapio(attrs['escola'], attrs['data_de'])
        deve_existir_cardapio(attrs['escola'], attrs['data_para'])
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
        fields = ('uuid', 'motivo', 'observacao', 'data_de', 'data_para', 'escola')


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
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=MotivoSuspensao.objects.all()
    )

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        return data

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

    def validate_data_inicial(self, data):
        nao_pode_ser_no_passado(data)
        deve_pedir_com_antecedencia(data)
        return data

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


class QuantidadePorPeriodoSuspensaoAlimentacaoCreateSerializer(serializers.ModelSerializer):
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=PeriodoEscolar.objects.all()
    )
    tipos_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=TipoAlimentacao.objects.all()
    )

    class Meta:
        model = QuantidadePorPeriodoSuspensaoAlimentacao
        exclude = ('id', 'grupo_suspensao')


class GrupoSuspensaoAlimentacaoCreateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(slug_field='uuid',
                                          queryset=Escola.objects.all()
                                          )
    quantidades_por_periodo = QuantidadePorPeriodoSuspensaoAlimentacaoCreateSerializer(many=True)
    suspensoes_alimentacao = SuspensaoAlimentacaoCreateSerializer(many=True)

    def create(self, validated_data):
        quantidades_por_periodo_array = validated_data.pop('quantidades_por_periodo')
        suspensoes_alimentacao_array = validated_data.pop('suspensoes_alimentacao')
        validated_data['criado_por'] = self.context['request'].user

        quantidades = []
        for quantidade_json in quantidades_por_periodo_array:
            quantidade = QuantidadePorPeriodoSuspensaoAlimentacaoCreateSerializer().create(quantidade_json)
            quantidades.append(quantidade)

        suspensoes = []
        for suspensao_json in suspensoes_alimentacao_array:
            suspensao = SuspensaoAlimentacaoCreateSerializer().create(suspensao_json)
            suspensoes.append(suspensao)

        grupo = GrupoSuspensaoAlimentacao.objects.create(**validated_data)
        grupo.quantidades_por_periodo.set(quantidades)
        grupo.suspensoes_alimentacao.set(suspensoes)
        return grupo

    def update(self, instance, validated_data):
        quantidades_por_periodo_array = validated_data.pop('quantidades_por_periodo')
        suspensoes_alimentacao_array = validated_data.pop('suspensoes_alimentacao')

        instance.quantidades_por_periodo.all().delete()
        instance.suspensoes_alimentacao.all().delete()

        quantidades = []
        for quantidade_json in quantidades_por_periodo_array:
            quantidade = QuantidadePorPeriodoSuspensaoAlimentacaoCreateSerializer().create(quantidade_json)
            quantidades.append(quantidade)

        suspensoes = []
        for suspensao_json in suspensoes_alimentacao_array:
            suspensao = SuspensaoAlimentacaoCreateSerializer().create(suspensao_json)
            suspensoes.append(suspensao)

        update_instance_from_dict(instance, validated_data, save=True)
        instance.quantidades_por_periodo.set(quantidades)
        instance.suspensoes_alimentacao.set(suspensoes)

        return instance

    class Meta:
        model = GrupoSuspensaoAlimentacao
        exclude = ('id',)
