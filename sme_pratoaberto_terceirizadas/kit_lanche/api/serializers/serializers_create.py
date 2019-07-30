from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_pratoaberto_terceirizadas.dados_comuns.validators import nao_pode_ser_no_passado
from sme_pratoaberto_terceirizadas.escola.models import Escola, DiretoriaRegional
from sme_pratoaberto_terceirizadas.kit_lanche.api.validators import valida_quantidade_kits_tempo_passeio, \
    escola_quantidade_nao_deve_ter_kits_e_tempo_passeio
from sme_pratoaberto_terceirizadas.kit_lanche.models import EscolaQuantidade
from ..validators import (
    solicitacao_deve_ter_1_ou_mais_kits,
    solicitacao_deve_ter_0_kit,
    valida_tempo_passeio_lista_igual,
    valida_tempo_passeio_lista_nao_igual,
    escola_quantidade_deve_ter_1_ou_mais_kits
)
from ... import models


class SolicitacaoKitLancheCreationSerializer(serializers.ModelSerializer):
    kits = serializers.SlugRelatedField(
        slug_field='uuid', many=True,
        required=True,
        queryset=models.KitLanche.objects.all())
    tempo_passeio_explicacao = serializers.CharField(
        source='get_tempo_passeio_display',
        required=False,
        read_only=True)

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        return data

    def validate(self, attrs):
        tempo_passeio = attrs.get('tempo_passeio')
        qtd_kits = len(attrs.get('kits'))
        valida_quantidade_kits_tempo_passeio(tempo_passeio, qtd_kits)
        return attrs

    def create(self, validated_data):
        kits = validated_data.pop('kits', [])
        solicitacao_kit_lanche = models.SolicitacaoKitLanche.objects.create(**validated_data)
        solicitacao_kit_lanche.kits.set(kits)
        return solicitacao_kit_lanche

    def update(self, instance, validated_data):
        kits = validated_data.pop('kits', [])
        update_instance_from_dict(instance, validated_data)
        instance.kits.set(kits)
        instance.save()

        return instance

    class Meta:
        model = models.SolicitacaoKitLanche
        exclude = ('id',)


class SolicitacaoKitLancheAvulsaCreationSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheCreationSerializer(
        required=True
    )
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Escola.objects.all()
    )

    def create(self, validated_data):
        solicitacao_kit_lanche_json = validated_data.pop('solicitacao_kit_lanche')
        solicitacao_kit_lanche = SolicitacaoKitLancheCreationSerializer(
        ).create(solicitacao_kit_lanche_json)

        solicitacao_kit_avulsa = models.SolicitacaoKitLancheAvulsa.objects.create(
            solicitacao_kit_lanche=solicitacao_kit_lanche, **validated_data
        )
        return solicitacao_kit_avulsa

    def update(self, instance, validated_data):
        solicitacao_kit_lanche_json = validated_data.pop('solicitacao_kit_lanche')
        solicitacao_kit_lanche = instance.solicitacao_kit_lanche

        SolicitacaoKitLancheCreationSerializer(
        ).update(solicitacao_kit_lanche, solicitacao_kit_lanche_json)

        update_instance_from_dict(instance, validated_data)

        instance.save()
        return instance

    class Meta:
        model = models.SolicitacaoKitLancheAvulsa
        exclude = ('id',)


class EscolaQuantidadeCreationSerializer(serializers.ModelSerializer):
    kits = serializers.SlugRelatedField(
        slug_field='uuid', many=True,
        required=True,
        queryset=models.KitLanche.objects.all())
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Escola.objects.all()
    )

    tempo_passeio_explicacao = serializers.CharField(
        source='get_tempo_passeio_display',
        required=False,
        read_only=True)

    solicitacao_unificada = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=models.SolicitacaoKitLancheUnificada.objects.all()
    )

    def validate(self, attrs):
        qtd_kits = len(attrs.get('kits'))
        tempo_passeio = attrs.get('tempo_passeio')
        valida_quantidade_kits_tempo_passeio(tempo_passeio, qtd_kits)
        return attrs

    def create(self, validated_data):
        kits = validated_data.pop('kits', [])
        escola_quantiade = EscolaQuantidade.objects.create(**validated_data)
        escola_quantiade.kits.set(kits)
        return escola_quantiade

    def update(self, instance, validated_data):
        kits = validated_data.pop('kits', [])
        update_instance_from_dict(instance, validated_data)
        instance.kits.set(kits)
        instance.save()
        return instance

    class Meta:
        model = EscolaQuantidade
        exclude = ('id',)


class SolicitacaoKitLancheUnificadaCreationSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheCreationSerializer(
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
    escolas_quantidades = EscolaQuantidadeCreationSerializer(
        many=True,
        required=False
    )

    def create(self, validated_data):
        lista_igual = validated_data.get('lista_kit_lanche_igual', True)
        solicitacao_kit_lanche = validated_data.pop('solicitacao_kit_lanche')
        escolas_quantidades = validated_data.pop('escolas_quantidades')

        solicitacao_base = SolicitacaoKitLancheCreationSerializer().create(solicitacao_kit_lanche)

        if not lista_igual:
            solicitacao_base.kits.set([])

        lista_quantidade_escola = self._gera_escolas_quantidades(escolas_quantidades)

        solicitacao_kit_unificada = models.SolicitacaoKitLancheUnificada.objects.create(
            solicitacao_kit_lanche=solicitacao_base, **validated_data
        )
        solicitacao_kit_unificada.vincula_escolas_quantidades(lista_quantidade_escola)
        return solicitacao_kit_unificada

    def update(self, instance, validated_data):
        escolas_quantidades = validated_data.pop('escolas_quantidades')
        solicitacao_kit_lanche_json = validated_data.pop('solicitacao_kit_lanche')

        solicitacao_kit_lanche = instance.solicitacao_kit_lanche
        instance.escolas_quantidades.all().delete()

        SolicitacaoKitLancheCreationSerializer().update(solicitacao_kit_lanche, solicitacao_kit_lanche_json)

        lista_quantidade_escola = self._gera_escolas_quantidades(escolas_quantidades)

        instance.vincula_escolas_quantidades(lista_quantidade_escola)

        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    def validate(self, data):

        self._valida_dados_base(data)
        self._valida_escolas_quantidades(data)

        return data

    def _valida_dados_base(self, data):
        solicitacao_kit_lanche = data.get('solicitacao_kit_lanche')
        kits_base = solicitacao_kit_lanche.get('kits', [])
        lista_igual = data.get('lista_kit_lanche_igual', True)
        tempo_passeio_base = solicitacao_kit_lanche.get('tempo_passeio', None)

        if lista_igual:
            valida_tempo_passeio_lista_igual(tempo_passeio_base)
            solicitacao_deve_ter_1_ou_mais_kits(len(kits_base))
        else:
            valida_tempo_passeio_lista_nao_igual(tempo_passeio_base)
            solicitacao_deve_ter_0_kit(len(kits_base))

    def _valida_escolas_quantidades(self, data):
        escolas_quantidades = data.get('escolas_quantidades')
        lista_igual = data.get('lista_kit_lanche_igual', True)

        if lista_igual:
            cont = 0
            for escola_quantidade in escolas_quantidades:
                kits = escola_quantidade.get('kits')
                escola_quantidade_nao_deve_ter_kits_e_tempo_passeio(
                    num_kits=len(kits),
                    tempo_passeio=escola_quantidade.get('tempo_passeio'),
                    indice=cont
                )
                cont += 1
        else:
            cont = 0
            for escola_quantidade in escolas_quantidades:
                kits = escola_quantidade.get('kits')
                escola_quantidade_deve_ter_1_ou_mais_kits(len(kits), indice=cont)
                cont += 1

    def _gera_escolas_quantidades(self, escolas_quantidades):
        escola_quantidade_lista = []
        for escola_quantidade_json in escolas_quantidades:
            escola_quantidade_object = EscolaQuantidadeCreationSerializer(
            ).create(escola_quantidade_json)
            escola_quantidade_lista.append(escola_quantidade_object)
        return escola_quantidade_lista

    def _atualiza_escolas_quantidades(self, escolas_quantidades, escolas_quantidades_lista):
        # TODO: quando o o len dos dois for diferente, tratar esse diff...
        for index in range(len(escolas_quantidades)):
            EscolaQuantidadeCreationSerializer(
            ).update(instance=escolas_quantidades[index],
                     validated_data=escolas_quantidades_lista[index])

    class Meta:
        model = models.SolicitacaoKitLancheUnificada
        exclude = ('id',)
