from rest_framework import serializers

from sme_pratoaberto_terceirizadas.alimentacao.models import Cardapio, InverterDiaCardapio
from sme_pratoaberto_terceirizadas.school.api.serializers import SchoolSerializer
from sme_pratoaberto_terceirizadas.users.serializers import PublicUserSerializer


class CardapioSerializer(serializers.ModelSerializer):
    escolas = SchoolSerializer(many=True, read_only=True)

    class Meta:
        model = Cardapio
        fields = '__all__'


class InverterDiaCardapioSerializer(serializers.ModelSerializer):
    usuario = PublicUserSerializer(many=False)

    class Meta:
        model = InverterDiaCardapio
        fields = ['uuid', 'registro', 'usuario', 'data_de', 'data_para', 'descricao', 'status', 'registro',
                  'observacao']

    def validate(self, attrs):
        if InverterDiaCardapio.ja_existe(attrs):
            raise serializers.ValidationError({'error': 'Já existe uma solicitação registrada com estes dados'})
        if not InverterDiaCardapio.valida_usuario_escola(attrs.get('usuario')):
            raise serializers.ValidationError({'error': 'Nenhuma escola vinculada ao usuário'})
        if not InverterDiaCardapio.valida_feriado(attrs):
            raise serializers.ValidationError({'error': 'Não é possivel solicitar dia de feriado para inversão'})
        if not InverterDiaCardapio.valida_dia_atual(attrs):
            raise serializers.ValidationError({'error': 'Não é possivel solicitar dia de hoje para inversão'})
        return attrs
