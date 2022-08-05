from rest_framework import serializers

from sme_terceirizadas.escola.api.serializers import TipoUnidadeEscolarSerializer
from sme_terceirizadas.medicao_inicial.models import DiaSobremesaDoce
from sme_terceirizadas.perfil.api.serializers import UsuarioSerializer


class DiaSobremesaDoceSerializer(serializers.ModelSerializer):
    tipo_unidade = TipoUnidadeEscolarSerializer()
    criado_por = UsuarioSerializer()

    class Meta:
        model = DiaSobremesaDoce
        exclude = ('id',)
