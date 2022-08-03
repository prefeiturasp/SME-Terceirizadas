from rest_framework import serializers

from sme_terceirizadas.escola.api.serializers import TipoUnidadeEscolarSerializer
from sme_terceirizadas.medicao_inicial.models import DiaSobremesaDoce


class DiaSobremesaDoceSerializer(serializers.ModelSerializer):
    tipo_unidade = TipoUnidadeEscolarSerializer()

    class Meta:
        model = DiaSobremesaDoce
        exclude = ('id',)
