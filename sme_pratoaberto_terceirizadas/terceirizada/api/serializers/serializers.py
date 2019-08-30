from rest_framework import serializers

from ...models import (Edital, Terceirizada, Nutricionista, Contrato, VigenciaContrato)
from ....dados_comuns.api.serializers import ContatoSerializer
from ....escola.models import Lote, DiretoriaRegional


class NutricionistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutricionista
        exclude = ('id', 'terceirizada')


class TerceirizadaSerializer(serializers.ModelSerializer):
    nutricionistas = NutricionistaSerializer(many=True)

    class Meta:
        model = Terceirizada
        exclude = ('id',)


class LoteSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = ('uuid', 'nome',)


class DiretoriaRegionalSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiretoriaRegional
        fields = ('uuid', 'nome',)


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

    lotes = LoteSimplesSerializer(many=True)

    terceirizadas = TerceirizadaSimplesSerializer(many=True)

    diretorias_regionais = DiretoriaRegionalSimplesSerializer(many=True)

    class Meta:
        model = Contrato
        exclude = ('id',)


class EditalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        exclude = ('id',)


class EditalContratosSerializer(serializers.ModelSerializer):
    contratos = ContratoSerializer(many=True)

    class Meta:
        model = Edital
        exclude = ('id',)
