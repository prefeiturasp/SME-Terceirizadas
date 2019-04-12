from rest_framework import serializers
from sme_pratoaberto_terceirizadas.meal_kit.models import MealKit


class MealKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealKit
        fields = '__all__'
