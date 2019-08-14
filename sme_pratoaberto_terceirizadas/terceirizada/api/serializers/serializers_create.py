from rest_framework import serializers
from sme_pratoaberto_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_pratoaberto_terceirizadas.escola.models import Lote, DiretoriaRegional
from ...models import (Terceirizada, Nutricionista, VigenciaContrato, Contrato, Edital)


class NutricionistaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutricionista
        exclude = ('id', 'terceirizada')


class TerceirizadaCreateSerializer(serializers.ModelSerializer):
    lotes = serializers.SlugRelatedField(slug_field='uuid', many=True, queryset=Lote.objects.all())
    nutricionistas = NutricionistaCreateSerializer(many=True)

    def create(self, validated_data):
        nutricionistas_array = validated_data.pop('nutricionistas')
        lotes = validated_data.pop('lotes', [])
        terceirizada = Terceirizada.objects.create(**validated_data)
        terceirizada.lotes.set(lotes)
        for nutri_json in nutricionistas_array:
            nutricionista = NutricionistaCreateSerializer().create(nutri_json)
            nutricionista.terceirizada = terceirizada
            nutricionista.save()
        return terceirizada

    class Meta:
        model = Terceirizada
        exclude = ('id',)


class VigenciaContratoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VigenciaContrato
        exclude = ('id', 'contrato')


class ContratoCreateSerializer(serializers.ModelSerializer):
    lotes = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Lote.objects.all()
    )

    terceirizadas = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        many=True,
        queryset=Terceirizada.objects.all()
    )

    dres = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=DiretoriaRegional.objects.all()
    )

    vigencias = VigenciaContratoCreateSerializer(many=True)


    def create(self, validated_data):
        lotes_json = validated_data.pop('lotes', [])
        terceirizadas_json = validated_data.pop('terceirizadas', [])
        dres_json = validated_data.pop('dres', [])

        vigencias_array = validated_data.pop('vigencias')

        vigencias = []
        for vigencia_json in vigencias_array:
            vigencia = VigenciaContratoCreateSerializer().create(vigencia_json)
            vigencias.append(vigencia)

        contrato = Contrato.objects.create(**validated_data)
        contrato.vigencias.set(vigencias)

        contrato.lotes.set(lotes_json)
        contrato.terceirizadas.set(terceirizadas_json)
        contrato.dres.set(dres_json)

        return contrato

    def update(self, instance, validated_data):
        lotes_json = validated_data.pop('lotes', [])
        terceirizadas_json = validated_data.pop('terceirizadas', [])
        dres_json = validated_data.pop('dres', [])

        vigencias_array = validated_data.pop('vigencias')

        instance.vigencias.all().delete()

        vigencias = []
        for vigencia_json in vigencias_array:
            vigencia = VigenciaContratoCreateSerializer().create(vigencia_json)
            vigencias.append(vigencia)

        update_instance_from_dict(instance, validated_data, save=True)

        instance.contratos.set(vigencias)
        instance.lotes.set(lotes_json)
        instance.terceirizadas.set(terceirizadas_json)
        instance.dres.set(dres_json)

        return instance

    class Meta:
        model = Contrato
        exclude = ('id',)


class EditalContratosCreateSerializer(serializers.ModelSerializer):

    contratos = ContratoCreateSerializer(many=True)

    def create(self, validated_data):
        contratos_array = validated_data.pop('contratos')

        contratos = []
        for contrato_json in contratos_array:
            contrato = ContratoCreateSerializer().create(contrato_json)
            contratos.append(contrato)

        edital = Edital.objects.create(**validated_data)
        edital.contratos.set(contratos)
        return edital

    def update(self, instance, validated_data):
        contrato_array = validated_data.pop('contratos')

        instance.contratos.all().delete()

        contratos = []
        for contrato_json in contrato_array:
            contrato = ContratoCreateSerializer().create(contrato_json)
            contratos.append(contrato)

        update_instance_from_dict(instance, validated_data, save=True)

        instance.contratos.set(contratos)

        return instance

    class Meta:
        model = Edital
        exclude = ('id',)
