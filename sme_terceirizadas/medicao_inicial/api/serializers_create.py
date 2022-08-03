from rest_framework import serializers

from sme_terceirizadas.escola.models import TipoUnidadeEscolar
from sme_terceirizadas.medicao_inicial.models import DiaSobremesaDoce


class DiaSobremesaDoceCreateSerializer(serializers.ModelSerializer):
    tipo_unidade = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoUnidadeEscolar.objects.all()
    )

    class Meta:
        model = DiaSobremesaDoce
        exclude = ('id',)
