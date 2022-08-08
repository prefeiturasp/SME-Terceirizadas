from rest_framework import serializers

from sme_terceirizadas.escola.models import TipoUnidadeEscolar
from sme_terceirizadas.medicao_inicial.models import DiaSobremesaDoce
from sme_terceirizadas.perfil.models import Usuario


class DiaSobremesaDoceCreateSerializer(serializers.ModelSerializer):
    tipo_unidade = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoUnidadeEscolar.objects.all(),
        required=True,
    )

    criado_por = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Usuario.objects.all(),
        required=True
    )

    class Meta:
        model = DiaSobremesaDoce
        exclude = ('id',)


class DiaSobremesaDoceCreateManySerializer(serializers.ModelSerializer):
    tipo_unidades = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoUnidadeEscolar.objects.all(),
        many=True,
        required=True,
    )

    def create(self, validated_data):
        """Cria ou atualiza dias de sobremesa doce."""
        dia_sobremesa_doce = None
        DiaSobremesaDoce.objects.filter(data=validated_data['data']).exclude(
            tipo_unidade__in=validated_data['tipo_unidades']).delete()
        dias_sobremesa_doce = DiaSobremesaDoce.objects.filter(data=validated_data['data'])
        for tipo_unidade in validated_data['tipo_unidades']:
            if not dias_sobremesa_doce.filter(tipo_unidade=tipo_unidade).exists():
                dia_sobremesa_doce = DiaSobremesaDoce(
                    criado_por=self.context['request'].user,
                    data=validated_data['data'],
                    tipo_unidade=tipo_unidade
                )
                dia_sobremesa_doce.save()
        return dia_sobremesa_doce

    class Meta:
        model = DiaSobremesaDoce
        fields = ('tipo_unidades', 'data', 'uuid')
