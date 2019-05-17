from rest_framework import serializers
from sme_pratoaberto_terceirizadas.meal_kit.models import MealKit, OrderMealKit


class MealKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealKit
        fields = '__all__'


class OrderMealKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMealKit
        field = '__all__'
