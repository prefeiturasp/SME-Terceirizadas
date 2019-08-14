from rest_framework import serializers

from ...models import (Edital, Terceirizada, Nutricionista, Contrato, VigenciaContrato)
from sme_pratoaberto_terceirizadas.dados_comuns.api.serializers import ContatoSerializer
from sme_pratoaberto_terceirizadas.escola.models import Lote, DiretoriaRegional


class NutricionistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutricionista
        exclude = ('id', 'terceirizada')


class TerceirizadaSerializer(serializers.ModelSerializer):
    nutricionistas = NutricionistaSerializer(many=True)

    class Meta:
        model = Terceirizada
        exclude = ('id',)


class TerceirizadaSimplesSerializer(serializers.ModelSerializer):
    contatos = ContatoSerializer(many=True)

    class Meta:
        model = Terceirizada
        fields = ('uuid', 'cnpj', 'nome_fantasia', 'contatos')


class VigenciaContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VigenciaContrato
        fields = ('uuid', 'data_inicial', 'data_final')


class ContratoSerializer(serializers.ModelSerializer):
    edital = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Edital.objects.all()
    )
    vigencias = VigenciaContratoSerializer(many=True)
    lotes = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Lote.objects.all(),
        many=True
    )
    terceirizadas = TerceirizadaSimplesSerializer(many=True)

    dres = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=DiretoriaRegional.objects.all(),
        many=True
    )

    class Meta:
        model = Contrato
        fields = ('uuid', 'numero', 'processo', 'data_proposta', 'lotes', 'terceirizadas', 'edital', 'vigencias', 'dres')


class EditalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        exclude = ('id',)


class EditalContratosSerializer(serializers.ModelSerializer):
    contratos = ContratoSerializer(many=True)

    class Meta:
        model = Edital
        exclude = ('id',)
