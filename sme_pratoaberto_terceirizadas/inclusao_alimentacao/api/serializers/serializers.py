from rest_framework import serializers

from sme_pratoaberto_terceirizadas.cardapio.api.serializers.serializers import TipoAlimentacaoSerializer
from sme_pratoaberto_terceirizadas.escola.api.serializers import EscolaSimplesSerializer
from sme_pratoaberto_terceirizadas.escola.api.serializers import PeriodoEscolarSerializer
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import (
    MotivoInclusaoContinua, MotivoInclusaoNormal,
    InclusaoAlimentacaoNormal, QuantidadePorPeriodo,
    GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua)


class MotivoInclusaoContinuaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoInclusaoContinua
        exclude = ('id',)


class MotivoInclusaoNormalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoInclusaoNormal
        exclude = ('id',)


class QuantidadePorPeriodoSerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSerializer()
    tipos_alimentacao = TipoAlimentacaoSerializer()

    class Meta:
        model = QuantidadePorPeriodo
        exclude = ('id',)


class InclusaoAlimentacaoNormalSerializer(serializers.ModelSerializer):
    motivo = MotivoInclusaoNormalSerializer()

    class Meta:
        model = InclusaoAlimentacaoNormal
        exclude = ('id',)


class InclusaoAlimentacaoContinuaSerializer(serializers.ModelSerializer):
    motivo = MotivoInclusaoContinuaSerializer()
    quantidades_periodo = QuantidadePorPeriodoSerializer(many=True)
    escola = EscolaSimplesSerializer()
    dias_semana_explicacao = serializers.CharField(
        source='dias_semana_display',
        required=False,
        read_only=True
    )

    class Meta:
        model = InclusaoAlimentacaoContinua
        exclude = ('id',)


class InclusaoAlimentacaoNormalSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InclusaoAlimentacaoNormal
        exclude = ('id', 'data')


class GrupoInclusaoAlimentacaoNormalSerializer(serializers.ModelSerializer):
    inclusoes = InclusaoAlimentacaoNormalSerializer(many=True)
    escola = EscolaSimplesSerializer()
    quantidades_periodo = QuantidadePorPeriodoSerializer(many=True)

    class Meta:
        model = GrupoInclusaoAlimentacaoNormal
        exclude = ('id',)
