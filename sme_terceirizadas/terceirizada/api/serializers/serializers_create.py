from rest_framework import serializers

from ....dados_comuns.api.serializers import ContatoSerializer
from ....dados_comuns.utils import update_instance_from_dict
from ....escola.api.serializers import UsuarioNutricionistaSerializer
from ....escola.models import DiretoriaRegional, Lote
from ....perfil.api.serializers import UsuarioUpdateSerializer
from ...models import Contrato, Edital, Nutricionista, Terceirizada, VigenciaContrato


class NutricionistaCreateSerializer(serializers.ModelSerializer):
    contatos = ContatoSerializer(many=True)

    def create(self, validated_data):
        contatos = validated_data.pop('contatos', [])
        nutricionista = Nutricionista.objects.create(**validated_data)
        for contato_json in contatos:
            contato = ContatoSerializer().create(
                validated_data=contato_json)
            nutricionista.contatos.add(contato)
        return nutricionista

    class Meta:
        model = Nutricionista
        exclude = ('id', 'terceirizada')


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

    terceirizada = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Terceirizada.objects.all()
    )

    diretorias_regionais = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=DiretoriaRegional.objects.all()
    )

    vigencias = VigenciaContratoCreateSerializer(many=True)

    def create(self, validated_data):
        lotes_json = validated_data.pop('lotes', [])
        dres_json = validated_data.pop('diretorias_regionais', [])
        vigencias_array = validated_data.pop('vigencias')

        vigencias = []
        for vigencia_json in vigencias_array:
            vigencia = VigenciaContratoCreateSerializer().create(vigencia_json)
            vigencias.append(vigencia)

        contrato = Contrato.objects.create(**validated_data)
        contrato.vigencias.set(vigencias)
        contrato.lotes.set(lotes_json)
        contrato.diretorias_regionais.set(dres_json)

        return contrato

    def update(self, instance, validated_data):
        lotes_json = validated_data.pop('lotes', [])
        terceirizadas_json = validated_data.pop('terceirizadas', [])
        dres_json = validated_data.pop('diretorias_regionais', [])

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
        instance.diretorias_regionais.set(dres_json)

        return instance

    class Meta:
        model = Contrato
        exclude = ('id',)


class TerceirizadaCreateSerializer(serializers.ModelSerializer):
    lotes = serializers.SlugRelatedField(slug_field='uuid', many=True, queryset=Lote.objects.all())
    nutricionistas = UsuarioNutricionistaSerializer(many=True)
    contatos = ContatoSerializer(many=True)

    def create(self, validated_data):
        nutricionistas_array = validated_data.pop('nutricionistas')
        lotes = validated_data.pop('lotes', [])
        contatos = validated_data.pop('contatos', [])
        terceirizada = Terceirizada.objects.create(**validated_data)
        terceirizada.lotes.set(lotes)
        for contato_json in contatos:
            contato = ContatoSerializer().create(
                validated_data=contato_json)
            terceirizada.contatos.add(contato)
        for nutri_json in nutricionistas_array:
            UsuarioUpdateSerializer().create_nutricionista(terceirizada, nutri_json)
        return terceirizada

    def update(self, instance, validated_data):
        # TODO: voltar aqui quando uma terceirizada tiver seu painel admin para criar suas nutris
        # aqui está tratando nutris como um dado escravo da Terceirizada
        nutricionistas_array = validated_data.pop('nutricionistas', [])
        lotes_array = validated_data.pop('lotes', [])
        contato_array = validated_data.pop('contatos', [])

        instance.contatos.all().delete()
        instance.desvincular_lotes()

        for nutri_json in nutricionistas_array:
            UsuarioUpdateSerializer().update_nutricionista(instance, nutri_json)

        contatos = []
        for contato_json in contato_array:
            contato = ContatoSerializer().create(contato_json)
            contatos.append(contato)

        update_instance_from_dict(instance, validated_data, save=True)

        instance.contatos.set(contatos)
        instance.lotes.set(lotes_array)

        return instance

    class Meta:
        model = Terceirizada
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
