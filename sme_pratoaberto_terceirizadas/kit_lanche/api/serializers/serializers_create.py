from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.validators import deve_ter_1_ou_mais_kits, deve_ter_0_kit, \
    valida_tempo_passeio_lista_igual, valida_tempo_passeio_lista_nao_igual
from sme_pratoaberto_terceirizadas.escola.models import Escola, DiretoriaRegional
from ... import models


def update_instance_from_dict(instance, attrs):
    for attr, val in attrs.items():
        setattr(instance, attr, val)


class SolicitacaoKitLancheCreationSerializer(serializers.ModelSerializer):
    kits = serializers.SlugRelatedField(
        slug_field='uuid', many=True,
        required=True,
        queryset=models.KitLanche.objects.all())
    tempo_passeio_explicacao = serializers.CharField(
        source='get_tempo_passeio_display',
        required=False,
        read_only=True)

    class Meta:
        model = models.SolicitacaoKitLanche
        exclude = ('id', 'uuid')


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
        kits = dado_base.pop('kits', [])
        solicitacao_base = models.SolicitacaoKitLanche.objects.create(**dado_base)
        solicitacao_base.kits.set(kits)

        solicitacao_kit_avulsa = models.SolicitacaoKitLancheAvulsa.objects.create(
            dado_base=solicitacao_base, **validated_data
        )
        return solicitacao_kit_avulsa

    def update(self, instance, validated_data):
        dado_base = validated_data.pop('dado_base')
        kits = dado_base.pop('kits', [])

        solicitacao_base = instance.dado_base
        update_instance_from_dict(solicitacao_base, dado_base)
        if kits:
            solicitacao_base.kits.set(kits)
        update_instance_from_dict(instance, validated_data)

        instance.save()
        return instance

    class Meta:
        model = models.SolicitacaoKitLancheAvulsa
        exclude = ('id',)


class SolicitacaoKitLancheUnificadaCreationSerializer(serializers.ModelSerializer):
    dado_base = SolicitacaoKitLancheCreationSerializer(
        required=False
    )
    motivo = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=models.MotivoSolicitacaoUnificada.objects.all()
    )
    diretoria_regional = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=DiretoriaRegional.objects.all()
    )

    def create(self, validated_data):
        dado_base = validated_data.pop('dado_base')
        kits = dado_base.pop('kits', [])
        solicitacao_base = models.SolicitacaoKitLanche.objects.create(**dado_base)
        solicitacao_base.kits.set(kits)

        solicitacao_kit_unificada = models.SolicitacaoKitLancheUnificada.objects.create(
            dado_base=solicitacao_base, **validated_data
        )
        return solicitacao_kit_unificada

    def update(self, instance, validated_data):
        dado_base = validated_data.pop('dado_base')
        kits = dado_base.pop('kits', [])

        solicitacao_base = instance.dado_base
        update_instance_from_dict(solicitacao_base, dado_base)
        solicitacao_base.kits.set(kits)
        update_instance_from_dict(instance, validated_data)

        instance.save()
        return instance

    def validate(self, data):
        dado_base = data.get('dado_base')
        kits = dado_base.get('kits', [])
        lista_igual = data.get('lista_kit_lanche_igual', True)
        tempo_passeio = dado_base.get('tempo_passeio', None)

        valida_tempo_passeio_lista_igual(lista_igual, tempo_passeio)
        valida_tempo_passeio_lista_nao_igual(lista_igual, tempo_passeio)
        if lista_igual:
            deve_ter_1_ou_mais_kits(lista_igual, len(kits))
        else:
            deve_ter_0_kit(lista_igual, len(kits))
        return data

    class Meta:
        model = models.SolicitacaoKitLancheUnificada
        exclude = ('id',)
