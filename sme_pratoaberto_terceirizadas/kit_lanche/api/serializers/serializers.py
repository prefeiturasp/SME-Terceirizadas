from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from sme_pratoaberto_terceirizadas.escola.api.serializers import (
    EscolaSimplesSerializer, DiretoriaRegionalSimplissimaSerializer
)
from ...models import (
    MotivoSolicitacaoUnificada, ItemKitLanche, KitLanche,
    SolicitacaoKitLanche, SolicitacaoKitLancheAvulsa,
    EscolaQuantidade, SolicitacaoKitLancheUnificada
)


class MotivoSolicitacaoUnificadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoSolicitacaoUnificada
        exclude = ('id',)


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

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id',)


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
    motivo = MotivoSolicitacaoUnificadaSerializer()
    solicitacao_kit_lanche = SolicitacaoKitLancheSimplesSerializer()
    escolas_quantidades = EscolaQuantidadeSerializerSimples(many=True)
    id_externo = serializers.CharField()
    total_kit_lanche = serializers.IntegerField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = SolicitacaoKitLancheUnificada
        exclude = ('id',)


class EscolaQuantidadeSerializer(serializers.ModelSerializer):
    kits = KitLancheSimplesSerializer(many=True, required=False)
    escola = EscolaSimplesSerializer()

    # solicitacao_unificada = SolicitacaoKitLancheUnificadaSerializer()

    class Meta:
        model = EscolaQuantidade
        exclude = ('id',)
