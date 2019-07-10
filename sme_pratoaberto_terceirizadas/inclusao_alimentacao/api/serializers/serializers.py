from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.api.serializers import DiaSemanaSerializer
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

    # TODO: esperar app cardapio.
    # tipos_alimentacao = TipoAlimentacao

    class Meta:
        model = QuantidadePorPeriodo
        exclude = ('id',)


class InclusaoAlimentacaoNormalSerializer(serializers.ModelSerializer):
    motivo = MotivoInclusaoNormalSerializer()
    quantidades_periodo = QuantidadePorPeriodoSerializer()

    class Meta:
        model = InclusaoAlimentacaoNormal
        exclude = ('id',)


class InclusaoAlimentacaoContinuaSerializer(serializers.ModelSerializer):
    motivo = MotivoInclusaoContinuaSerializer()
    quantidades_periodo = QuantidadePorPeriodoSerializer(many=True)
    escola = EscolaSimplesSerializer()
    dias_semana = DiaSemanaSerializer(many=True)

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

    class Meta:
        model = GrupoInclusaoAlimentacaoNormal
        exclude = ('id',)
