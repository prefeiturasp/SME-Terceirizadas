from rest_framework import serializers

from ....cardapio.api.serializers.serializers import TipoAlimentacaoSimplesSerializer
from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....escola.api.serializers import (
    EscolaSimplesSerializer,
    EscolaSimplissimaSerializer,
    FaixaEtariaSerializer,
    PeriodoEscolarSerializer,
    PeriodoEscolarSimplesSerializer
)
from ....escola.models import FaixaEtaria
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
from ....terceirizada.api.serializers.serializers import TerceirizadaSimplesSerializer
from ...models import (
    DiasMotivosInclusaoDeAlimentacaoCEMEI,
    InclusaoDeAlimentacaoCEMEI,
    QuantidadeDeAlunosEMEIInclusaoDeAlimentacaoCEMEI,
    QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoCEMEI
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
    faixa_etaria = FaixaEtariaSerializer()
    periodo = PeriodoEscolarSimplesSerializer()

    class Meta:
        model = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI
        exclude = ('id', 'inclusao_alimentacao_da_cei')


class InclusaoAlimentacaoDaCEISerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    prioridade = serializers.CharField()
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    tipos_alimentacao = TipoAlimentacaoSimplesSerializer(many=True, read_only=True)
    motivo = MotivoInclusaoNormalSerializer()
    quantidade_alunos_por_faixas_etarias = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEISerializer(
        many=True, read_only=True)
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    id_externo = serializers.CharField()
    escola = EscolaSimplesSerializer()

    def to_representation(self, instance):
        retorno = super().to_representation(instance)

        # Inclui o total de alunos nas faixas etárias num período
        faixas_etarias_da_solicitacao = FaixaEtaria.objects.filter(
            uuid__in=[
                f['faixa_etaria__uuid'] for f in
                instance.quantidade_alunos_por_faixas_etarias.values('faixa_etaria__uuid')
            ]
        )

        qtde_alunos = instance.escola.alunos_por_periodo_e_faixa_etaria(
            instance.data,
            faixas_etarias_da_solicitacao
        )

        nome_periodo = 'INTEGRAL'
        for faixa_etaria in retorno['quantidade_alunos_por_faixas_etarias']:
            uuid_faixa_etaria = faixa_etaria['faixa_etaria']['uuid']
            faixa_etaria['total_alunos_no_periodo'] = qtde_alunos[nome_periodo][uuid_faixa_etaria]

        return retorno

    class Meta:
        model = InclusaoAlimentacaoDaCEI
        exclude = ('id',)


class QuantidadePorPeriodoSerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSerializer()
    tipos_alimentacao = TipoAlimentacaoSimplesSerializer(many=True, read_only=True)

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
    rastro_terceirizada = TerceirizadaSimplesSerializer()

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
    rastro_terceirizada = TerceirizadaSimplesSerializer()
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


class DiasMotivosInclusaoDeAlimentacaoCEMEISerializer(serializers.ModelSerializer):
    motivo = MotivoInclusaoNormalSerializer()

    class Meta:
        model = DiasMotivosInclusaoDeAlimentacaoCEMEI
        exclude = ('id',)


class QuantidadeDeAlunosEMEIInclusaoDeAlimentacaoCEMEISerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSimplesSerializer()

    class Meta:
        model = QuantidadeDeAlunosEMEIInclusaoDeAlimentacaoCEMEI
        exclude = ('id',)


class QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoCEMEISerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    faixa_etaria = FaixaEtariaSerializer()

    class Meta:
        model = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoCEMEI
        exclude = ('id',)


class InclusaoDeAlimentacaoCEMEISerializer(serializers.ModelSerializer):
    escola = EscolaSimplissimaSerializer()
    dias_motivos_da_inclusao_cemei = DiasMotivosInclusaoDeAlimentacaoCEMEISerializer(many=True)
    quantidade_alunos_cei_da_inclusao_cemei = (
        QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoCEMEISerializer(many=True))
    quantidade_alunos_emei_da_inclusao_cemei = QuantidadeDeAlunosEMEIInclusaoDeAlimentacaoCEMEISerializer(many=True)
    id_externo = serializers.CharField()

    class Meta:
        model = InclusaoDeAlimentacaoCEMEI
        exclude = ('id',)


class InclusaoDeAlimentacaoCEMEIRetrieveSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    dias_motivos_da_inclusao_cemei = DiasMotivosInclusaoDeAlimentacaoCEMEISerializer(many=True)
    quantidade_alunos_cei_da_inclusao_cemei = (
        QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoCEMEISerializer(many=True))
    quantidade_alunos_emei_da_inclusao_cemei = QuantidadeDeAlunosEMEIInclusaoDeAlimentacaoCEMEISerializer(many=True)
    id_externo = serializers.CharField()
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    prioridade = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = InclusaoDeAlimentacaoCEMEI
        exclude = ('id',)
