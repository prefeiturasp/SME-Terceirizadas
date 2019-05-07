from rest_framework import serializers

from sme_pratoaberto_terceirizadas.food_inclusion.models import FoodInclusion, FoodInclusionDescription


class FoodInclusionDescriptionSerializer(serializers.ModelSerializer):
    # TODO recuperar dados em vez de id.
    class Meta:
        model = FoodInclusionDescription
        fields = '__all__'


class FoodInclusionSerializer(serializers.ModelSerializer):
    # TODO recuperar dados em vez de id.
    descriptions = serializers.SerializerMethodField()

    def get_descriptions(self, obj):
        return FoodInclusionDescriptionSerializer(obj.foodinclusiondescription_set.all(), many=True).data

    class Meta:
        model = FoodInclusion
        fields = ('uuid', 'descriptions', 'date', 'reason', 'date_from', 'date_to', 'weekdays', 'status', 'obs')
