from rest_framework import serializers

from sme_pratoaberto_terceirizadas.common_data.models import EmailConfiguration
from ..models import WorkingDays


class WorkingDaysSerializer(serializers.Serializer):
    date_five_working_days = serializers.DateField()
    date_two_working_days = serializers.DateField()

    def create(self, validated_data):
        return WorkingDays(id=None, **validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance


class EmailConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfiguration
        fields = ('username', 'email')
