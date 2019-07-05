from rest_framework import serializers

from sme_pratoaberto_terceirizadas.dados_comuns.validators import solicitacao_deve_ter_1_ou_mais_kits, \
    solicitacao_deve_ter_0_kit, \
    valida_tempo_passeio_lista_igual, valida_tempo_passeio_lista_nao_igual, escola_quantidade_deve_ter_0_kit, \
    escola_quantidade_deve_ter_mesmo_tempo_passeio, escola_quantidade_deve_ter_1_ou_mais_kits
from sme_pratoaberto_terceirizadas.escola.models import Escola, DiretoriaRegional
from sme_pratoaberto_terceirizadas.kit_lanche.models import EscolaQuantidade
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
        exclude = ('id', 'uuid')


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

    class Meta:
        model = EscolaQuantidade
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
    escolas_quantidades = EscolaQuantidadeCreationSerializer(
        many=True,
        required=False
    )

    def create(self, validated_data):
        lista_igual = validated_data.get('lista_kit_lanche_igual', True)
        dado_base = validated_data.pop('dado_base')
        escolas_quantidades = validated_data.pop('escolas_quantidades')

        kits = dado_base.pop('kits', [])
        solicitacao_base = models.SolicitacaoKitLanche.objects.create(**dado_base)

        if lista_igual:
            solicitacao_base.kits.set(kits)

        lista_quantidade_escola = self._gera_escolas_quantidades(escolas_quantidades)

        solicitacao_kit_unificada = models.SolicitacaoKitLancheUnificada.objects.create(
            dado_base=solicitacao_base, **validated_data
        )
        solicitacao_kit_unificada.vincula_escolas_quantidades(lista_quantidade_escola)
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

        self._valida_dados_base(data)
        self._valida_escolas_quantidades(data)

        return data

    def _valida_dados_base(self, data):
        dado_base = data.get('dado_base')
        kits_base = dado_base.get('kits', [])
        lista_igual = data.get('lista_kit_lanche_igual', True)
        tempo_passeio_base = dado_base.get('tempo_passeio', None)

        if lista_igual:
            valida_tempo_passeio_lista_igual(tempo_passeio_base)
            solicitacao_deve_ter_1_ou_mais_kits(len(kits_base))
        else:
            valida_tempo_passeio_lista_nao_igual(tempo_passeio_base)
            solicitacao_deve_ter_0_kit(len(kits_base))

    def _valida_escolas_quantidades(self, data):
        escolas_quantidades = data.get('escolas_quantidades')
        lista_igual = data.get('lista_kit_lanche_igual', True)
        dado_base = data.get('dado_base')

        if lista_igual:
            cont = 0
            for escola_quantidade in escolas_quantidades:
                kits = escola_quantidade.get('kits')
                escola_quantidade_deve_ter_0_kit(len(kits), indice=cont)
                escola_quantidade_deve_ter_mesmo_tempo_passeio(
                    escola_quantidade,
                    dado_base,
                    indice=cont)
                cont += 1
        else:
            cont = 0
            for escola_quantidade in escolas_quantidades:
                kits = escola_quantidade.get('kits')
                escola_quantidade_deve_ter_1_ou_mais_kits(len(kits), indice=cont)
                cont += 1

    def _gera_escolas_quantidades(self, escolas_quantidades):
        objetos_lista = []
        for escola_quantidade in escolas_quantidades:
            kits_personalizados_da_escola = escola_quantidade.pop('kits', [])
            escola_quantidade_object = models.EscolaQuantidade.objects.create(**escola_quantidade)
            escola_quantidade_object.kits.set(kits_personalizados_da_escola)
            objetos_lista.append(escola_quantidade_object)

        return objetos_lista

    class Meta:
        model = models.SolicitacaoKitLancheUnificada
        exclude = ('id',)
