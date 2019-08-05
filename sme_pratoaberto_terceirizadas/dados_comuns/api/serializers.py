from des.models import DynamicEmailConfiguration
from rest_framework import serializers

from ..models import TemplateMensagem


class ConfiguracaoEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicEmailConfiguration
        fields = ('host', 'port', 'username', 'password',
                  'from_email', 'use_tls', 'use_ssl', 'timeout')


class ConfiguracaoMensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateMensagem
        exclude = ('id', 'tipo')
