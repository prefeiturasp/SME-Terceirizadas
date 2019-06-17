from rest_framework import serializers

from sme_pratoaberto_terceirizadas.escola.models import Escola, PeriodoEscolar
from sme_pratoaberto_terceirizadas.food.api.serializers import MealTypeSerializer


class EscolaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Escola
        fields = '__all__'


class PeriodoEscolarSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    tipo_refeicao = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.nome

    def get_tipo_refeicao(self, obj):
        return MealTypeSerializer(obj.meal_types.all(), many=True).data

    class Meta:
        model = PeriodoEscolar
        fields = ('label', 'valor', 'tipo_refeicao' )
