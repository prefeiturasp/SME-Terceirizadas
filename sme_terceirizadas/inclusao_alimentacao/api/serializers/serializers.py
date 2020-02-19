from rest_framework import serializers

from .utils import monta_label_de_faixa_etaria

from ....cardapio.api.serializers.serializers import CombosVinculoTipoAlimentoSimplesSerializer, \
    CombosVinculoTipoAlimentoSimplissimaSerializer
from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....escola.api.serializers import EscolaSimplesSerializer, PeriodoEscolarSerializer, \
    PeriodoEscolarSimplesSerializer, EscolaListagemSimplesSelializer
from ....inclusao_alimentacao.models import (
    GrupoInclusaoAlimentacaoNormal,
    InclusaoAlimentacaoContinua,
    InclusaoAlimentacaoDaCEI,
    InclusaoAlimentacaoNormal,
    MotivoInclusaoContinua,
    MotivoInclusaoNormal,
    QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI,
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


class QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEISerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        faixa_etaria = obj.faixa_etaria
        return monta_label_de_faixa_etaria(faixa_etaria.inicio, faixa_etaria.fim)

    class Meta:
        model = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI
        exclude = ('id', 'inclusao_alimentacao_da_cei', 'faixa_etaria')


class InclusaoAlimentacaoDaCEISerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    tipos_alimentacao = CombosVinculoTipoAlimentoSimplissimaSerializer(many=True, read_only=True)
    motivo = MotivoInclusaoNormalSerializer()
    faixas_etarias = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEISerializer(many=True, read_only=True)

    class Meta:
        model = InclusaoAlimentacaoDaCEI
        exclude = ('id', 'escola', 'criado_por')


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
