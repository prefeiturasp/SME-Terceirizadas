from rest_framework import serializers

from ...models import (
    EscolaQuantidade, ItemKitLanche, KitLanche, SolicitacaoKitLanche,
    SolicitacaoKitLancheAvulsa, SolicitacaoKitLancheUnificada
)
from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....escola.api.serializers import (
    DiretoriaRegionalSimplissimaSerializer, EscolaSimplesSerializer
)


class ItemKitLancheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemKitLanche
        exclude = ('id',)


class KitLancheSerializer(serializers.ModelSerializer):
    itens = ItemKitLancheSerializer(many=True)

    class Meta:
        model = KitLanche
        exclude = ('id',)


class KitLancheSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitLanche
        exclude = ('id', 'itens')


class SolicitacaoKitLancheSimplesSerializer(serializers.ModelSerializer):
    kits = KitLancheSimplesSerializer(many=True, required=False)
    prioridade = serializers.CharField()
    tempo_passeio_explicacao = serializers.CharField(source='get_tempo_passeio_display',
                                                     required=False,
                                                     read_only=True)

    class Meta:
        model = SolicitacaoKitLanche
        exclude = ('id',)


class SolicitacaoKitLancheAvulsaSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheSimplesSerializer()
    escola = EscolaSimplesSerializer(read_only=True,
                                     required=False)
    prioridade = serializers.CharField()
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    quantidade_alimentacoes = serializers.IntegerField()
    data = serializers.DateField()

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id',)


class SolicitacaoKitLancheAvulsaSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()
    id_externo = serializers.CharField()

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id', 'solicitacao_kit_lanche', 'escola', 'criado_por')


class EscolaQuantidadeSerializerSimples(serializers.ModelSerializer):
    kits = KitLancheSimplesSerializer(many=True, required=False)
    escola = EscolaSimplesSerializer()
    solicitacao_unificada = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=SolicitacaoKitLancheUnificada.objects.all())
    tempo_passeio_explicacao = serializers.CharField(source='get_tempo_passeio_display',
                                                     required=False,
                                                     read_only=True)

    class Meta:
        model = EscolaQuantidade
        exclude = ('id',)


class SolicitacaoKitLancheUnificadaSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSimplissimaSerializer()
    solicitacao_kit_lanche = SolicitacaoKitLancheSimplesSerializer()
    escolas_quantidades = EscolaQuantidadeSerializerSimples(many=True)
    id_externo = serializers.CharField()
    # TODO: remover total_kit_lanche ou quantidade_alimentacoes. estao duplicados
    total_kit_lanche = serializers.IntegerField()
    lote_nome = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    prioridade = serializers.CharField()
    data = serializers.DateField()
    quantidade_alimentacoes = serializers.IntegerField()

    class Meta:
        model = SolicitacaoKitLancheUnificada
        exclude = ('id',)


class SolicitacaoKitLancheUnificadaSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()

    class Meta:
        model = SolicitacaoKitLancheUnificada
        exclude = ('id',)


class EscolaQuantidadeSerializer(serializers.ModelSerializer):
    kits = KitLancheSimplesSerializer(many=True, required=False)
    escola = EscolaSimplesSerializer()

    class Meta:
        model = EscolaQuantidade
        exclude = ('id',)
