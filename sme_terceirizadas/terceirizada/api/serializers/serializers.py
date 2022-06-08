from rest_framework import serializers

from ....dados_comuns.api.serializers import ContatoSerializer
from ....escola.models import DiretoriaRegional, Lote
from ...models import Contrato, Edital, Nutricionista, Terceirizada, VigenciaContrato


class NutricionistaSerializer(serializers.ModelSerializer):
    contatos = ContatoSerializer(many=True)

    class Meta:
        model = Nutricionista
        exclude = ('id', 'terceirizada')


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


class DistribuidorSimplesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Terceirizada
        fields = ('uuid', 'nome_fantasia', 'razao_social')


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

    terceirizada = TerceirizadaSimplesSerializer()

    diretorias_regionais = DiretoriaRegionalSimplesSerializer(many=True)

    class Meta:
        model = Contrato
        exclude = ('id',)


class EditalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        exclude = ('id',)


class EditalSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        fields = ('uuid', 'numero')


class EditalContratosSerializer(serializers.ModelSerializer):
    contratos = ContratoSerializer(many=True)

    class Meta:
        model = Edital
        exclude = ('id',)


class ContratoSimplesSerializer(serializers.ModelSerializer):
    edital = EditalSerializer()

    class Meta:
        model = Contrato
        exclude = ('id', 'terceirizada', 'diretorias_regionais', 'lotes')
