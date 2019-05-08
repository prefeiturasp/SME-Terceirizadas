from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food.api.serializers import MealTypeSerializer
from sme_pratoaberto_terceirizadas.food_inclusion.models import FoodInclusion, FoodInclusionDescription


class FoodInclusionDescriptionSerializer(serializers.ModelSerializer):
    period = serializers.SerializerMethodField()
    food_inclusion = serializers.SerializerMethodField()
    meal_type = serializers.SerializerMethodField()

    def get_period(self, obj):
        return obj.period.name

    def get_food_inclusion(self, obj):
        return obj.food_inclusion.uuid

    def get_meal_type(self, obj):
        return MealTypeSerializer(obj.meal_type.all(), many=True).data

    class Meta:
        model = FoodInclusionDescription
        exclude = ('id',)


class FoodInclusionSerializer(serializers.ModelSerializer):
    descriptions = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_descriptions(self, obj):
        return FoodInclusionDescriptionSerializer(obj.foodinclusiondescription_set.all(), many=True).data

    def get_reason(self, obj):
        return obj.reason.name

    def get_status(self, obj):
        return obj.status.name

    class Meta:
        model = FoodInclusion
        fields = ('uuid', 'descriptions', 'date', 'reason', 'date_from', 'date_to', 'weekdays', 'status', 'obs',
                  'priority')
