from rest_framework import serializers

from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio, InverterDiaCardapio
from sme_pratoaberto_terceirizadas.school.api.serializers import SchoolSerializer


class CardapioSerializer(serializers.ModelSerializer):
    escolas = SchoolSerializer(many=True, read_only=True)

    class Meta:
        model = Cardapio
        fields = '__all__'


class InverterDiaCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = InverterDiaCardapio
        fields = '__all__'

    def create(self, validated_data):
        if not InverterDiaCardapio.valida_usuario_escola(validated_data.get('usuario')):
            raise serializers.ValidationError('Nenhuma escola vinculada ao usuário')
        if not InverterDiaCardapio.valida_feriado(validated_data):
            raise serializers.ValidationError('Não é possivel solicitar de feriado para inversão')
        if not InverterDiaCardapio.valida_dia_atual(validated_data):
            raise serializers.ValidationError('Não é possivel solicitar dia de hoje para inversão')





