from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food.models import MealType


class MealTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealType
        fields = ('name',)
