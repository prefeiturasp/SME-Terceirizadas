from rest_framework import serializers

from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....escola.api.serializers import (
    EscolaListagemSimplesSelializer,
    EscolaSimplesSerializer,
    FaixaEtariaSerializer,
    PeriodoEscolarSerializer,
    PeriodoEscolarSimplesSerializer,
    TipoUnidadeEscolarSerializer,
    TipoUnidadeEscolarSerializerSimples
)
from ....escola.models import FaixaEtaria
from ....terceirizada.api.serializers.serializers import EditalSerializer, TerceirizadaSimplesSerializer
from ...models import (
    AlteracaoCardapio,
    AlteracaoCardapioCEI,
    Cardapio,
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    FaixaEtariaSubstituicaoAlimentacaoCEI,
    GrupoSuspensaoAlimentacao,
    HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar,
    InversaoCardapio,
    MotivoAlteracaoCardapio,
    MotivoDRENaoValida,
    MotivoSuspensao,
    QuantidadePorPeriodoSuspensaoAlimentacao,
    SubstituicaoAlimentacaoNoPeriodoEscolar,
    SubstituicaoAlimentacaoNoPeriodoEscolarCEI,
    SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    SuspensaoAlimentacao,
    SuspensaoAlimentacaoDaCEI,
    SuspensaoAlimentacaoNoPeriodoEscolar,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
)


class TipoAlimentacaoSerializer(serializers.ModelSerializer):
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
        fields = ('uuid', 'tipos_alimentacao', 'combo', 'label',)


class CombosVinculoTipoAlimentoSimplesSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSimplesSerializer(many=True)
    substituicoes = SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializer(many=True)
    vinculo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.all()
    )
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        label = ''
        for tipo_alimentacao in obj.tipos_alimentacao.all():
            if len(label) == 0:
                label += tipo_alimentacao.nome
            else:
                label += f' e {tipo_alimentacao.nome}'
        return label

    class Meta:
        model = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = ('uuid', 'tipos_alimentacao', 'vinculo', 'substituicoes', 'label',)


class CombosVinculoTipoAlimentoSimplissimaSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        label = ''
        for tipo_alimentacao in obj.tipos_alimentacao.all():
            if len(label) == 0:
                label += tipo_alimentacao.nome
            else:
                label += f' e {tipo_alimentacao.nome}'
        return label

    class Meta:
        model = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = ('uuid', 'label',)


class HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarSerializer(serializers.ModelSerializer):
    escola = EscolaListagemSimplesSelializer()
    tipo_alimentacao = TipoAlimentacaoSerializer()
    periodo_escolar = PeriodoEscolarSimplesSerializer()

    class Meta:
        model = HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar
        fields = ('uuid', 'hora_inicial', 'hora_final', 'escola', 'tipo_alimentacao', 'periodo_escolar')


class VinculoTipoAlimentoSimplesSerializer(serializers.ModelSerializer):
    tipo_unidade_escolar = TipoUnidadeEscolarSerializerSimples()
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True, read_only=True)

    class Meta:
        model = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
        fields = ('uuid', 'tipo_unidade_escolar', 'periodo_escolar', 'tipos_alimentacao')


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
    data = serializers.DateField()  # representa data do objeto, a menor entre data_de e data_para
    data_de = serializers.DateField()
    data_para = serializers.DateField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()

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


class SuspensaoAlimentacaoDaCEISerializer(serializers.ModelSerializer):
    escola = EscolaListagemSimplesSelializer()
    motivo = MotivoSuspensaoSerializer()
    periodos_escolares = PeriodoEscolarSimplesSerializer(many=True)
    id_externo = serializers.CharField()

    class Meta:
        model = SuspensaoAlimentacaoDaCEI
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
    rastro_terceirizada = TerceirizadaSimplesSerializer()

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


class FaixaEtariaSubstituicaoAlimentacaoCEISerializer(serializers.ModelSerializer):
    faixa_etaria = FaixaEtariaSerializer()

    class Meta:
        model = FaixaEtariaSubstituicaoAlimentacaoCEI
        exclude = ('id',)


class SubstituicoesAlimentacaoNoPeriodoEscolarSerializerBase(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSerializer()
    alteracao_cardapio = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AlteracaoCardapio.objects.all()
    )
    tipos_alimentacao_de = TipoAlimentacaoSerializer(many=True)


class SubstituicoesAlimentacaoNoPeriodoEscolarSerializer(SubstituicoesAlimentacaoNoPeriodoEscolarSerializerBase):
    tipos_alimentacao_para = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = SubstituicaoAlimentacaoNoPeriodoEscolar
        exclude = ('id',)


class SubstituicoesAlimentacaoNoPeriodoEscolarCEISerializer(SubstituicoesAlimentacaoNoPeriodoEscolarSerializerBase):
    tipos_alimentacao_para = TipoAlimentacaoSerializer()

    faixas_etarias = FaixaEtariaSubstituicaoAlimentacaoCEISerializer(many=True)

    def to_representation(self, instance):
        retorno = super().to_representation(instance)

        faixas_etarias_da_solicitacao = FaixaEtaria.objects.filter(
            uuid__in=[f.faixa_etaria.uuid for f in instance.faixas_etarias.all()]
        )

        # Inclui o total de alunos nas faixas etárias num período
        qtde_alunos = instance.alteracao_cardapio.escola.alunos_por_periodo_e_faixa_etaria(
            instance.alteracao_cardapio.data,
            faixas_etarias_da_solicitacao
        )
        nome_periodo = 'INTEGRAL' if instance.periodo_escolar.nome == 'PARCIAL' else instance.periodo_escolar.nome
        for faixa_etaria in retorno['faixas_etarias']:
            uuid_faixa_etaria = faixa_etaria['faixa_etaria']['uuid']
            faixa_etaria['total_alunos_no_periodo'] = qtde_alunos[nome_periodo][uuid_faixa_etaria]

        return retorno

    class Meta:
        model = SubstituicaoAlimentacaoNoPeriodoEscolarCEI
        exclude = ('id',)


class AlteracaoCardapioSerializerBase(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    motivo = MotivoAlteracaoCardapioSerializer()
    foi_solicitado_fora_do_prazo = serializers.BooleanField()
    eh_alteracao_com_lanche_repetida = serializers.BooleanField()
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    prioridade = serializers.CharField()


class AlteracaoCardapioSerializer(AlteracaoCardapioSerializerBase):
    substituicoes = SubstituicoesAlimentacaoNoPeriodoEscolarSerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = AlteracaoCardapio
        exclude = ('id',)


class AlteracaoCardapioCEISerializer(AlteracaoCardapioSerializerBase):
    substituicoes = SubstituicoesAlimentacaoNoPeriodoEscolarCEISerializer(many=True)

    class Meta:
        model = AlteracaoCardapioCEI
        exclude = ('id',)


class AlteracaoCardapioSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()

    class Meta:
        model = AlteracaoCardapio
        exclude = ('id', 'criado_por', 'escola', 'motivo')


class MotivoDRENaoValidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoDRENaoValida
        exclude = ('id',)
