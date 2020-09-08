from des.models import DynamicEmailConfiguration
from rest_framework import serializers

from ...perfil.api.serializers import UsuarioSerializer
from ..models import (
    AnexoLogSolicitacoesUsuario,
    CategoriaPerguntaFrequente,
    Contato,
    LogSolicitacoesUsuario,
    PerguntaFrequente,
    TemplateMensagem
)


class AnexoLogSolicitacoesUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexoLogSolicitacoesUsuario
        fields = ('nome', 'arquivo')


class LogSolicitacoesUsuarioComAnexosSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    anexos = serializers.SerializerMethodField()
    status_evento_explicacao = serializers.CharField(
        source='get_status_evento_display',
        required=False,
        read_only=True
    )

    def get_anexos(self, obj):
        return AnexoLogSolicitacoesUsuarioSerializer(
            AnexoLogSolicitacoesUsuario.objects.filter(
                log=obj
            ), many=True
        ).data

    class Meta:
        model = LogSolicitacoesUsuario
        fields = (
            'anexos', 'status_evento_explicacao', 'usuario', 'criado_em', 'descricao', 'justificativa',
            'resposta_sim_nao')


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

class LogSolicitacoesSerializer(serializers.ModelSerializer):
    status_evento_explicacao = serializers.CharField(
        source='get_status_evento_display',
        required=False,
        read_only=True
    )

    class Meta:
        model = LogSolicitacoesUsuario
        fields = ('status_evento_explicacao', 'criado_em', 'descricao', 'justificativa', 'resposta_sim_nao')


class LogSolicitacoesUsuarioComVinculoSerializer(LogSolicitacoesUsuarioSerializer):
    nome_instituicao = serializers.CharField(source='usuario.vinculo_atual.instituicao.nome')

    class Meta:
        model = LogSolicitacoesUsuario
        fields = ('status_evento_explicacao', 'usuario', 'criado_em', 'descricao',
                  'justificativa', 'resposta_sim_nao', 'nome_instituicao')


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
