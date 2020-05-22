from des.models import DynamicEmailConfiguration
from rest_framework import serializers

from ...perfil.api.serializers import UsuarioSerializer
from ..models import CategoriaPerguntaFrequente, Contato, LogSolicitacoesUsuario, PerguntaFrequente, TemplateMensagem


class LogSolicitacoesUsuarioSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    status_evento_explicacao = serializers.CharField(
        source='get_status_evento_display',
        required=False,
        read_only=True
    )

    class Meta:
        model = LogSolicitacoesUsuario
        fields = ('status_evento_explicacao', 'usuario', 'criado_em', 'descricao', 'justificativa', 'resposta_sim_nao')


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


class CategoriaPerguntaFrequenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPerguntaFrequente
        exclude = ('id',)


class PerguntaFrequenteCreateSerializer(serializers.ModelSerializer):
    categoria = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=CategoriaPerguntaFrequente.objects.all()
    )

    class Meta:
        model = PerguntaFrequente
        exclude = ('id', 'criado_em')


class PerguntaFrequenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerguntaFrequente
        exclude = ('id', 'categoria', 'criado_em')


class ConsultaPerguntasFrequentesSerializer(serializers.ModelSerializer):
    perguntas = PerguntaFrequenteSerializer(many=True, source='perguntafrequente_set', read_only=True)

    class Meta:
        model = CategoriaPerguntaFrequente
        exclude = ('id',)
