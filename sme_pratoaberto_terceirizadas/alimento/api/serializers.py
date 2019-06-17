from rest_framework import serializers

from sme_pratoaberto_terceirizadas.alimento.models import TipoRefeicao, Refeicao


class TipoRefeicaoSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.nome

    def get_value(self, obj):
        return obj.nome

    class Meta:
        model = TipoRefeicao
        fields = ('label', 'value')


class RefeicaoSerializer(serializers.ModelSerializer):
    foods = serializers.StringRelatedField(many=True)

    class Meta:
        model = Refeicao
        fields = ['uuid', 'titulo', 'alimentos']
