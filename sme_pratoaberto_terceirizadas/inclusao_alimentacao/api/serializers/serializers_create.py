from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.models import DiaSemana
from sme_pratoaberto_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_pratoaberto_terceirizadas.dados_comuns.validators import nao_pode_ser_passado
from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar, Escola
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import (
    MotivoInclusaoContinua, MotivoInclusaoNormal,
    InclusaoAlimentacaoNormal, QuantidadePorPeriodo, InclusaoAlimentacaoContinua, GrupoInclusaoAlimentacaoNormal)


class MotivoInclusaoContinuaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoInclusaoContinua
        exclude = ('id',)


class MotivoInclusaoNormalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoInclusaoNormal
        exclude = ('id',)


class QuantidadePorPeriodoCreationSerializer(serializers.ModelSerializer):
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=PeriodoEscolar.objects.all())

    # TODO: esperar app cardapio.
    # tipos_alimentacao = TipoAlimentacao

    def create(self, validated_data):
        tipos_alimentacao = validated_data.pop('tipos_alimentacao', [])
        quantidade_periodo = QuantidadePorPeriodo.objects.create(**validated_data)
        quantidade_periodo.tipos_alimentacao.set(tipos_alimentacao)
        return quantidade_periodo

    def update(self, instance, validated_data):
        tipos_alimentacao = validated_data.pop('tipos_alimentacao', [])
        if tipos_alimentacao:
            instance.tipos_alimentacao.set(tipos_alimentacao)
        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = QuantidadePorPeriodo
        exclude = ('id', 'tipos_alimentacao')


class InclusaoAlimentacaoNormalCreationSerializer(serializers.ModelSerializer):
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=MotivoInclusaoNormal.objects.all())
    quantidade_periodo = QuantidadePorPeriodoCreationSerializer()

    def validate_data(self, data):
        nao_pode_ser_passado(data)
        return data

    def create(self, validated_data):
        quantidades_periodo_json = validated_data.pop('quantidade_periodo')
        quantidade_periodo = QuantidadePorPeriodoCreationSerializer(
        ).create(quantidades_periodo_json)
        inclusao_alimentacao_normal_obj = InclusaoAlimentacaoNormal.objects.create(
            quantidade_periodo=quantidade_periodo, **validated_data)
        return inclusao_alimentacao_normal_obj

    def update(self, instance, validated_data):
        quantidade_periodo_json = validated_data.pop('quantidade_periodo')
        quantidade_periodo = instance.quantidade_periodo
        QuantidadePorPeriodoCreationSerializer(
        ).update(quantidade_periodo, quantidade_periodo_json)
        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = InclusaoAlimentacaoNormal
        exclude = ('id',)


class GrupoInclusaoAlimentacaoNormalCreationSerializer(serializers.ModelSerializer):
    inclusoes = InclusaoAlimentacaoNormalCreationSerializer(many=True)
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )

    def create(self, validated_data):
        inclusoes_json = validated_data.pop('inclusoes')
        inclusoes_lista = []
        for inclusao_json in inclusoes_json:
            inc = InclusaoAlimentacaoNormalCreationSerializer(
            ).create(validated_data=inclusao_json)
            inclusoes_lista.append(inc)
        grupo_inclusao_alimentacao_normal = GrupoInclusaoAlimentacaoNormal.objects.create(**validated_data)
        grupo_inclusao_alimentacao_normal.inclusoes.set(inclusoes_lista)
        return grupo_inclusao_alimentacao_normal

    def update(self, instance, validated_data):
        inclusoes_dict = validated_data.pop('inclusoes')
        inclusoes = instance.inclusoes.all()
        assert len(inclusoes) == len(inclusoes_dict)
        for index in range(len(inclusoes_dict)):
            InclusaoAlimentacaoNormalCreationSerializer(
            ).update(instance=inclusoes[index], validated_data=inclusoes_dict[index])
        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = GrupoInclusaoAlimentacaoNormal
        exclude = ('id',)


class InclusaoAlimentacaoContinuaCreationSerializer(serializers.ModelSerializer):
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=MotivoInclusaoContinua.objects.all())
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    quantidades_periodo = QuantidadePorPeriodoCreationSerializer(many=True)
    dias_semana = serializers.PrimaryKeyRelatedField(
        many=True, queryset=DiaSemana.objects.all()
    )

    def create(self, validated_data):
        quantidades_periodo_array = validated_data.pop('quantidades_periodo')

        lista_escola_quantidade = self._gera_lista_escola_quantidade(quantidades_periodo_array)
        dias_semana = validated_data.pop('dias_semana', [])

        inclusao_alimentacao_continua = InclusaoAlimentacaoContinua.objects.create(
            **validated_data)

        inclusao_alimentacao_continua.dias_semana.set(dias_semana)
        inclusao_alimentacao_continua.quantidades_periodo.set(lista_escola_quantidade)

        return inclusao_alimentacao_continua

    def _gera_lista_escola_quantidade(self, quantidades_periodo_array):
        objetos_lista = []
        for quantidade_periodo in quantidades_periodo_array:
            tipos_alimentacao = quantidade_periodo.pop('tipos_alimentacao', [])
            quantidades_periodo_obj = QuantidadePorPeriodo.objects.create(**quantidade_periodo)
            quantidades_periodo_obj.tipos_alimentacao.set(tipos_alimentacao)
            objetos_lista.append(quantidades_periodo_obj)
        return objetos_lista

    class Meta:
        model = InclusaoAlimentacaoContinua
        exclude = ('id',)
