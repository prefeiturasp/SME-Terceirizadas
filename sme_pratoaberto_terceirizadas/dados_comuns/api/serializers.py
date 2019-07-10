from des.models import DynamicEmailConfiguration
from rest_framework import serializers

from ..models import DiaSemana


class ConfiguracaoEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicEmailConfiguration
        fields = ('host', 'port', 'username', 'password',
                  'from_email', 'use_tls', 'use_ssl', 'timeout')


class DiaSemanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaSemana
        exclude = ('uuid', 'numero')
