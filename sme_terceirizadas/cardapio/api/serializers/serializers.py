from rest_framework import serializers

from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....escola.api.serializers import (
    EscolaListagemSimplesSelializer,
    EscolaSimplesSerializer,
    PeriodoEscolarSerializer,
    PeriodoEscolarSimplesSerializer,
    TipoUnidadeEscolarSerializer
)
from ....terceirizada.api.serializers.serializers import EditalSerializer
from ...models import (
    AlteracaoCardapio,
    Cardapio,
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    GrupoSuspensaoAlimentacao,
    InversaoCardapio,
    MotivoAlteracaoCardapio,
    MotivoSuspensao,
    QuantidadePorPeriodoSuspensaoAlimentacao,
    SubstituicaoAlimentacaoNoPeriodoEscolar,
    SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    SuspensaoAlimentacao,
    SuspensaoAlimentacaoNoPeriodoEscolar,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
)


class SubstituicoesTipoAlimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlimentacao
        exclude = ('id', 'substituicoes',)


class TipoAlimentacaoSerializer(serializers.ModelSerializer):
    substituicoes = SubstituicoesTipoAlimentacaoSerializer(many=True)

    class Meta:
        model = TipoAlimentacao
        exclude = ('id',)


class TipoAlimentacaoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlimentacao
        fields = ('uuid', 'nome',)


class SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSimplesSerializer(many=True)
    combo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all()
    )

    class Meta:
        model = SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = ('uuid', 'tipos_alimentacao', 'combo')


class CombosVinculoTipoAlimentoSimplesSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSimplesSerializer(many=True)
    substituicoes = SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializer(many=True)
    vinculo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.all()
    )

    class Meta:
        model = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = ('uuid', 'tipos_alimentacao', 'vinculo', 'substituicoes')


class VinculoTipoAlimentoSimplesSerializer(serializers.ModelSerializer):
    tipo_unidade_escolar = TipoUnidadeEscolarSerializer()
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    combos = CombosVinculoTipoAlimentoSimplesSerializer(many=True)

    class Meta:
        model = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
        fields = ('uuid', 'tipo_unidade_escolar', 'periodo_escolar', 'combos')


class CardapioSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cardapio
        exclude = ('id',)


class CardapioSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True, read_only=True)
    tipos_unidade_escolar = TipoUnidadeEscolarSerializer(many=True, read_only=True)
    edital = EditalSerializer()

    class Meta:
        model = Cardapio
        exclude = ('id',)


class InversaoCardapioSerializer(serializers.ModelSerializer):
    cardapio_de = CardapioSimplesSerializer()
    cardapio_para = CardapioSimplesSerializer()
    escola = EscolaSimplesSerializer()
    id_externo = serializers.CharField()
    prioridade = serializers.CharField()
    data_de = serializers.DateField()
    data_para = serializers.DateField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = InversaoCardapio
        exclude = ('id', 'criado_por')


class InversaoCardapioSimpleserializer(serializers.ModelSerializer):
    id_externo = serializers.CharField()
    prioridade = serializers.CharField()
    escola = EscolaSimplesSerializer()
    data = serializers.DateField()

    class Meta:
        model = InversaoCardapio
        exclude = ('id', 'criado_por', 'cardapio_de', 'cardapio_para',)


class MotivoSuspensaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoSuspensao
        exclude = ('id',)


class SuspensaoAlimentacaoNoPeriodoEscolarSerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = SuspensaoAlimentacaoNoPeriodoEscolar
        exclude = ('id', 'suspensao_alimentacao')


class SuspensaoAlimentacaoSerializer(serializers.ModelSerializer):
    motivo = MotivoSuspensaoSerializer()

    class Meta:
        model = SuspensaoAlimentacao
        exclude = ('id', 'grupo_suspensao')


class QuantidadePorPeriodoSuspensaoAlimentacaoSerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = QuantidadePorPeriodoSuspensaoAlimentacao
        exclude = ('id', 'grupo_suspensao')


class GrupoSuspensaoAlimentacaoSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    quantidades_por_periodo = QuantidadePorPeriodoSuspensaoAlimentacaoSerializer(many=True)
    suspensoes_alimentacao = SuspensaoAlimentacaoSerializer(many=True)
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = GrupoSuspensaoAlimentacao
        exclude = ('id',)


class GrupoSuspensaoAlimentacaoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoSuspensaoAlimentacao
        exclude = ('id', 'criado_por', 'escola')


class GrupoSupensaoAlimentacaoListagemSimplesSerializer(serializers.ModelSerializer):
    escola = EscolaListagemSimplesSelializer()
    prioridade = serializers.CharField()

    class Meta:
        model = GrupoSuspensaoAlimentacao
        fields = ('uuid', 'id_externo', 'status', 'prioridade', 'criado_em', 'escola',)


class MotivoAlteracaoCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoAlteracaoCardapio
        exclude = ('id',)


class SubstituicoesAlimentacaoNoPeriodoEscolarSerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSerializer()
    alteracao_cardapio = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AlteracaoCardapio.objects.all()
    )
    tipo_alimentacao_de = TipoAlimentacaoSerializer()
    tipo_alimentacao_para = TipoAlimentacaoSerializer()

    class Meta:
        model = SubstituicaoAlimentacaoNoPeriodoEscolar
        exclude = ('id',)


class AlteracaoCardapioSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    motivo = MotivoAlteracaoCardapioSerializer()
    substituicoes = SubstituicoesAlimentacaoNoPeriodoEscolarSerializer(many=True)
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    prioridade = serializers.CharField()

    class Meta:
        model = AlteracaoCardapio
        exclude = ('id',)


class AlteracaoCardapioSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()

    class Meta:
        model = AlteracaoCardapio
        exclude = ('id', 'criado_por', 'escola', 'motivo')
