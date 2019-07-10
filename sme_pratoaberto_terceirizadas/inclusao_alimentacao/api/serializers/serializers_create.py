from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import (
    MotivoInclusaoContinua, MotivoInclusaoNormal,
    InclusaoAlimentacaoNormal, QuantidadePorPeriodo)


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

    class Meta:
        model = QuantidadePorPeriodo
        exclude = ('id', 'tipos_alimentacao')


class InclusaoAlimentacaoNormalCreationSerializer(serializers.ModelSerializer):
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=MotivoInclusaoNormal.objects.all())
    quantidades_periodo = QuantidadePorPeriodoCreationSerializer()

    def create(self, validated_data):
        quantidades_periodo = validated_data.pop('quantidades_periodo')
        tipos_alimentacao = quantidades_periodo.pop('tipos_alimentacao', [])
        quantidades_periodo_obj = QuantidadePorPeriodo.objects.create(**quantidades_periodo)
        quantidades_periodo_obj.tipos_alimentacao.set(tipos_alimentacao)
        inclusao_alimentacao_normal_obj = InclusaoAlimentacaoNormal.objects.create(
            quantidades_periodo=quantidades_periodo_obj, **validated_data)
        return inclusao_alimentacao_normal_obj

    def update(self, instance, validated_data):
        quantidades_periodo = validated_data.pop('quantidades_periodo')
        tipos_alimentacao = quantidades_periodo.pop('tipos_alimentacao', [])

        quantidades_periodo_obj = instance.quantidades_periodo
        update_instance_from_dict(quantidades_periodo_obj, quantidades_periodo)
        if tipos_alimentacao:
            quantidades_periodo_obj.tipos_alimentacao.set(tipos_alimentacao)
        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance


    class Meta:
        model = InclusaoAlimentacaoNormal
        exclude = ('id',)
