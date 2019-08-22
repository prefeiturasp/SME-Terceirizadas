from rest_framework import serializers

from ...models import (
    TipoAlimentacao, Cardapio, InversaoCardapio,
    SuspensaoAlimentacao, AlteracaoCardapio, MotivoAlteracaoCardapio,
    SubstituicoesAlimentacaoNoPeriodoEscolar,
    SuspensaoAlimentacaoNoPeriodoEscolar, GrupoSuspensaoAlimentacao,
    QuantidadePorPeriodoSuspensaoAlimentacao, MotivoSuspensao
)
from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....escola.api.serializers import (
    EscolaSimplesSerializer, PeriodoEscolarSerializer,
    TipoUnidadeEscolarSerializer,
    PeriodoEscolarSimplesSerializer
)
from ....terceirizada.api.serializers.serializers import EditalSerializer


class TipoAlimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlimentacao
        exclude = ('id',)


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
    status = serializers.SerializerMethodField()
    id_externo = serializers.CharField()
    prioridade = serializers.CharField()
    data_de = serializers.DateField()
    data_para = serializers.DateField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = InversaoCardapio
        exclude = ('id', 'criado_por')


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

    class Meta:
        model = GrupoSuspensaoAlimentacao
        exclude = ('id',)


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
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = SubstituicoesAlimentacaoNoPeriodoEscolar
        exclude = ('id',)


class AlteracaoCardapioSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    motivo = MotivoAlteracaoCardapioSerializer()
    substituicoes = SubstituicoesAlimentacaoNoPeriodoEscolarSerializer(many=True)
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = AlteracaoCardapio
        exclude = ('id',)
