from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food.models import MealType


class MealTypeSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_label(self, obj):
        return obj.name

    def get_value(self, obj):
        return obj.name

    class Meta:
        model = MealType
        fields = ('label', 'value')
