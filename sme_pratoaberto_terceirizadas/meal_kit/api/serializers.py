from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food.api.serializers import MealSerializer
from sme_pratoaberto_terceirizadas.meal_kit.models import MealKit, OrderMealKit
from sme_pratoaberto_terceirizadas.school.api.serializers import SchoolSerializer


class MealKitSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = MealKit
        fields = ['uuid', 'name', 'is_active', 'meals']


class OrderMealKitSerializer(serializers.ModelSerializer):
    schools = SchoolSerializer(many=True, read_only=True)
    meal_kits = MealKitSerializer(many=True, read_only=True)

    class Meta:
        model = OrderMealKit
        fields = '__all__'
