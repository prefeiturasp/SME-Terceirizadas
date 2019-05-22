from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food.api.serializers import MealSerializer
from sme_pratoaberto_terceirizadas.meal_kit.models import MealKit, OrderMealKit


class MealKitSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = MealKit
        fields = ['uuid', 'name', 'is_active', 'meals']


class OrderMealKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMealKit
        field = '__all__'
