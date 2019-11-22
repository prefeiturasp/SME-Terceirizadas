from des.models import DynamicEmailConfiguration
from rest_framework import serializers

from ...perfil.api.serializers import UsuarioSerializer
from ..models import Contato, LogSolicitacoesUsuario, TemplateMensagem


class LogSolicitacoesUsuarioSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    status_evento_explicacao = serializers.CharField(
        source='get_status_evento_display',
        required=False,
        read_only=True
    )

    class Meta:
        model = LogSolicitacoesUsuario
        fields = ('status_evento_explicacao', 'usuario', 'criado_em', 'descricao', 'justificativa')


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
