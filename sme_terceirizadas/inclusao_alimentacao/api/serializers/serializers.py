from rest_framework import serializers

from ....cardapio.api.serializers.serializers import CombosVinculoTipoAlimentoSimplesSerializer
from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....escola.api.serializers import EscolaSimplesSerializer, PeriodoEscolarSerializer
from ....inclusao_alimentacao.models import (
    GrupoInclusaoAlimentacaoNormal,
    InclusaoAlimentacaoContinua,
    InclusaoAlimentacaoNormal,
    MotivoInclusaoContinua,
    MotivoInclusaoNormal,
    QuantidadePorPeriodo
)


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
    tipos_alimentacao = CombosVinculoTipoAlimentoSimplesSerializer(many=True, read_only=True)

    class Meta:
        model = QuantidadePorPeriodo
        exclude = ('id',)


class InclusaoAlimentacaoNormalSerializer(serializers.ModelSerializer):
    motivo = MotivoInclusaoNormalSerializer()

    class Meta:
        model = InclusaoAlimentacaoNormal
        exclude = ('id',)


class InclusaoAlimentacaoContinuaSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()
    motivo = MotivoInclusaoContinuaSerializer()
    quantidades_periodo = QuantidadePorPeriodoSerializer(many=True)
    escola = EscolaSimplesSerializer()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    dias_semana_explicacao = serializers.CharField(
        source='dias_semana_display',
        required=False,
        read_only=True
    )
    id_externo = serializers.CharField()

    class Meta:
        model = InclusaoAlimentacaoContinua
        exclude = ('id',)


class InclusaoAlimentacaoContinuaSimplesSerializer(serializers.ModelSerializer):
    motivo = MotivoInclusaoContinuaSerializer()
    dias_semana_explicacao = serializers.CharField(
        source='dias_semana_display',
        required=False,
        read_only=True
    )
    prioridade = serializers.CharField()

    class Meta:
        model = InclusaoAlimentacaoContinua
        exclude = ('id', 'escola', 'criado_por')


class InclusaoAlimentacaoNormalSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()

    class Meta:
        model = InclusaoAlimentacaoNormal
        exclude = ('id', 'data')


class GrupoInclusaoAlimentacaoNormalSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()
    inclusoes = InclusaoAlimentacaoNormalSerializer(many=True)
    escola = EscolaSimplesSerializer()
    quantidades_periodo = QuantidadePorPeriodoSerializer(many=True)
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    id_externo = serializers.CharField()

    class Meta:
        model = GrupoInclusaoAlimentacaoNormal
        exclude = ('id',)


class GrupoInclusaoAlimentacaoNormalSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()

    class Meta:
        model = GrupoInclusaoAlimentacaoNormal
        exclude = ('id', 'criado_por', 'escola')
