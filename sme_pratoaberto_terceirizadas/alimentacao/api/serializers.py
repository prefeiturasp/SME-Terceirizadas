from rest_framework import serializers

from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio, InverterDiaCardapio
from sme_pratoaberto_terceirizadas.escola.api.serializers import EscolaCompletaSerializer


class CardapioSerializer(serializers.ModelSerializer):
    escolas = EscolaCompletaSerializer(many=True, read_only=True)

    class Meta:
        model = Cardapio
        fields = '__all__'


class InverterDiaCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = InverterDiaCardapio
        fields = '__all__'

    def validate(self, attrs):
        if InverterDiaCardapio.ja_existe(attrs):
            raise serializers.ValidationError('Já existe uma solicitação registrada com estes dados')
        if not InverterDiaCardapio.valida_usuario_escola(attrs.get('usuario')):
            raise serializers.ValidationError('Nenhuma escola vinculada ao usuário')
        if not InverterDiaCardapio.valida_feriado(attrs):
            raise serializers.ValidationError('Não é possivel solicitar dia de feriado para inversão')
        if not InverterDiaCardapio.valida_dia_atual(attrs):
            raise serializers.ValidationError('Não é possivel solicitar dia de hoje para inversão')
        return attrs
