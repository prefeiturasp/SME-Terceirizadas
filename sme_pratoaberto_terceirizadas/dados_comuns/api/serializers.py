from des.models import DynamicEmailConfiguration
from rest_framework import serializers

from ..models import Contato, TemplateMensagem, LogSolicitacoesUsuario
from sme_pratoaberto_terceirizadas.perfil.api.serializers import UsuarioSerializer


class LogSolicitacoesUsuarioSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    status_evento_explicacao = serializers.CharField(
        source='get_status_evento_display',
        required=False,
        read_only=True
    )

    class Meta:
        model = LogSolicitacoesUsuario
        fields = ('status_evento_explicacao', 'usuario', 'criado_em')


class ConfiguracaoEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicEmailConfiguration
        fields = ('host', 'port', 'username', 'password',
                  'from_email', 'use_tls', 'use_ssl', 'timeout')


class ConfiguracaoMensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateMensagem
        exclude = ('id', 'tipo')


class ContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contato
        exclude = ('id',)
