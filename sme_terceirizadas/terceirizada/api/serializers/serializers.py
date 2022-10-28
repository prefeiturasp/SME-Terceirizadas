from rest_framework import serializers

from ....dados_comuns.api.serializers import ContatoSerializer
from ....escola.models import DiretoriaRegional, Lote
from ...models import (
    Contrato,
    Edital,
    EmailTerceirizadaPorModulo,
    Modulo,
    Nutricionista,
    Terceirizada,
    VigenciaContrato
)
from ...utils import serializa_emails_terceirizadas


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


class DistribuidorSimplesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Terceirizada
        fields = ('uuid', 'nome_fantasia', 'razao_social')


class VigenciaContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VigenciaContrato
        fields = ('uuid', 'data_inicial', 'data_final')


class EditalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        exclude = ('id',)


class ContratoSimplesSerializer(serializers.ModelSerializer):
    edital = EditalSerializer()

    class Meta:
        model = Contrato
        exclude = ('id', 'terceirizada', 'diretorias_regionais', 'lotes')


class TerceirizadaSimplesSerializer(serializers.ModelSerializer):
    contatos = ContatoSerializer(many=True)
    contratos = ContratoSimplesSerializer(many=True)

    class Meta:
        model = Terceirizada
        fields = ('uuid', 'cnpj', 'nome_fantasia', 'contatos', 'contratos')


class TerceirizadaLookUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Terceirizada
        fields = ('uuid', 'razao_social')


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


class EditalSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edital
        fields = ('uuid', 'numero')


class EditalContratosSerializer(serializers.ModelSerializer):
    contratos = ContratoSerializer(many=True)

    class Meta:
        model = Edital
        exclude = ('id',)


class ModuloSerializer(serializers.ModelSerializer):

    class Meta:
        model = Modulo
        exclude = ('id',)


class EmailsPorModuloSerializer(serializers.ModelSerializer):
    emails_terceirizadas = serializers.SerializerMethodField()

    def get_emails_terceirizadas(self, obj):
        busca = self.context['busca']
        emails = obj.emails_terceirizadas.all()
        if busca and busca.upper() not in obj.razao_social.upper():
            emails = emails.filter(email__icontains=busca)
        return serializa_emails_terceirizadas(emails)

    class Meta:
        model = Terceirizada
        fields = ('uuid', 'razao_social', 'emails_terceirizadas')


class EmailsTerceirizadaPorModuloSerializer(serializers.ModelSerializer):
    modulo = serializers.SerializerMethodField()
    terceirizada = serializers.SerializerMethodField()

    def get_modulo(self, obj):
        return obj.modulo.nome if obj.modulo else None

    def get_terceirizada(self, obj):
        return obj.terceirizada.razao_social if obj.terceirizada else None

    class Meta:
        model = EmailTerceirizadaPorModulo
        exclude = ('id', 'criado_por')


class CreateEmailTerceirizadaPorModuloSerializer(serializers.ModelSerializer):
    terceirizada = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Terceirizada.objects.all()
    )
    modulo = serializers.SlugRelatedField(
        slug_field='nome',
        required=True,
        queryset=Modulo.objects.all()
    )
    criado_por = serializers.CharField(required=False)

    def create(self, validated_data):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        validated_data['criado_por'] = user
        EmailTerceirizada = EmailTerceirizadaPorModulo.objects.create(**validated_data)
        return EmailTerceirizada

    class Meta:
        model = EmailTerceirizadaPorModulo
        exclude = ('id',)
