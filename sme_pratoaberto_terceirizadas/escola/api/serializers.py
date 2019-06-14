from rest_framework import serializers

from sme_pratoaberto_terceirizadas.escola.models import Escola, PeriodoEscolar
from sme_pratoaberto_terceirizadas.food.api.serializers import MealTypeSerializer


class EscolaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Escola
        fields = '__all__'


class SchoolPeriodSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    meal_types = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.name

    def get_meal_types(self, obj):
        return MealTypeSerializer(obj.meal_types.all(), many=True).data

    class Meta:
        model = PeriodoEscolar
        fields = ('label', 'value', 'meal_types')
