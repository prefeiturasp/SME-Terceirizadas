from des.models import DynamicEmailConfiguration
from rest_framework import serializers

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
        model = DynamicEmailConfiguration
        fields = ('host', 'port', 'username', 'password',
                  'from_email', 'use_tls', 'use_ssl', 'timeout')
