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


def update_instance_from_dict(instance, attrs):
    for attr, val in attrs.items():
        setattr(instance, attr, val)


class SolicitacaoKitLancheAvulsaCreationSerializer(serializers.ModelSerializer):
    dado_base = SolicitacaoKitLancheCreationSerializer(
        required=False
    )
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Escola.objects.all()
    )

    def create(self, validated_data):
        dado_base = validated_data.pop('dado_base')
        kits = dado_base.pop('kits')
        solicitacao_base = SolicitacaoKitLanche.objects.create(**dado_base)
        solicitacao_base.kits.set(kits)

        solicitacao_kit_avulsa = SolicitacaoKitLancheAvulsa.objects.create(
            dado_base=solicitacao_base, **validated_data
        )
        return solicitacao_kit_avulsa

    def update(self, instance, validated_data):
        dado_base = validated_data.pop('dado_base')
        kits = dado_base.pop('kits')

        solicitacao_base = instance.dado_base
        update_instance_from_dict(solicitacao_base, dado_base)
        solicitacao_base.kits.set(kits)
        update_instance_from_dict(instance, validated_data)

        instance.save()
        return instance

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id',)
