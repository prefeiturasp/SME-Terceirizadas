from des.models import DynamicEmailConfiguration
from rest_framework import serializers

from ..models import DiasUteis


class DiasUteisSerializer(serializers.Serializer):
    data_cinco_dias_uteis = serializers.DateField()
    data_dois_dias_uteis = serializers.DateField()

    def create(self, validated_data):
        return DiasUteis(id=None, **validated_data)

    def update(self, instance, validated_data):
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        return instance


class ConfiguracaoEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicEmailConfiguration
        fields = ('host', 'port', 'username', 'password',
                  'from_email', 'use_tls', 'use_ssl', 'timeout')
