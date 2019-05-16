from rest_framework import serializers

from sme_pratoaberto_terceirizadas.school.models import School, SchoolPeriod
from sme_pratoaberto_terceirizadas.food.api.serializers import MealTypeSerializer


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = '__all__'


class SchoolPeriodSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    meal_types = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.name

    def get_meal_types(self, obj):
        return MealTypeSerializer(obj.meal_types.all(), many=True).data

    class Meta:
        model = SchoolPeriod
        fields = ('label', 'value', 'meal_types')
