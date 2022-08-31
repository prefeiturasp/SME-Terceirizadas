import environ
from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from sme_terceirizadas.escola.api.serializers import TipoUnidadeEscolarSerializer
from sme_terceirizadas.medicao_inicial.models import (
    CategoriaMedicao,
    DiaSobremesaDoce,
    Responsavel,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)
from sme_terceirizadas.perfil.api.serializers import UsuarioSerializer


class DiaSobremesaDoceSerializer(serializers.ModelSerializer):
    tipo_unidade = TipoUnidadeEscolarSerializer()
    criado_por = UsuarioSerializer()

    class Meta:
        model = DiaSobremesaDoce
        exclude = ('id',)


class AnexoOcorrenciaMedicaoInicialSerializer(serializers.ModelSerializer):
    arquivo = serializers.SerializerMethodField()

    def get_arquivo(self, obj):
        env = environ.Env()
        api_url = env.str('URL_ANEXO', default='http://localhost:8000')
        return f'{api_url}{obj.arquivo.url}'

    class Meta:
        model = TipoContagemAlimentacao
        exclude = ('id',)


class TipoContagemAlimentacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoContagemAlimentacao
        exclude = ('id',)


class ResponsavelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Responsavel
        exclude = ('id', 'solicitacao_medicao_inicial',)


class SolicitacaoMedicaoInicialSerializer(serializers.ModelSerializer):
    escola = serializers.CharField(source='escola.nome')
    tipo_contagem_alimentacoes = TipoContagemAlimentacaoSerializer()
    responsaveis = ResponsavelSerializer(many=True)
    anexo = AnexoOcorrenciaMedicaoInicialSerializer(required=False)
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = SolicitacaoMedicaoInicial
        exclude = ('id', 'criado_por',)


class ValorMedicaoSerializer(serializers.ModelSerializer):
    medicao_uuid = serializers.SerializerMethodField()

    def get_medicao_uuid(self, obj):
        return obj.medicao.uuid

    class Meta:
        model = ValorMedicao
        fields = ('categoria_medicao', 'nome_campo', 'valor', 'dia', 'medicao_uuid', 'uuid')


class CategoriaMedicaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoriaMedicao
        fields = '__all__'
