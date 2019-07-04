from rest_framework import serializers

from sme_pratoaberto_terceirizadas.escola.models import Escola
from ...models import (
    SolicitacaoKitLanche, SolicitacaoKitLancheAvulsa, KitLanche)


class SolicitacaoKitLancheCreationSerializer(serializers.ModelSerializer):
    kits = serializers.SlugRelatedField(
        slug_field='uuid', many=True,
        required=False,
        queryset=KitLanche.objects.all())
    tempo_passeio_explicacao = serializers.CharField(
        source='get_tempo_passeio_display',
        required=False,
        read_only=True)

    class Meta:
        model = SolicitacaoKitLanche
        exclude = ('id',)


class SolicitacaoKitLancheAvulsaCreationSerializer(serializers.ModelSerializer):
    dado_base = SolicitacaoKitLancheCreationSerializer()
    escola = serializers.SlugRelatedField(slug_field='uuid', queryset=Escola.objects.all())

    def create(self, validated_data):
        dado_base = validated_data.pop('dado_base')
        kits = dado_base.pop('kits')
        kit_base = SolicitacaoKitLanche.objects.create(**dado_base)
        kit_base.kits.set(kits)
        solicitacao_kit_avulsa = SolicitacaoKitLancheAvulsa.objects.create(
            dado_base=kit_base, **validated_data
        )
        return solicitacao_kit_avulsa

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id',)
