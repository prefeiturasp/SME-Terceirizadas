import datetime

import environ
from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from sme_terceirizadas.dados_comuns.utils import converte_numero_em_mes
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
    anexos = AnexoOcorrenciaMedicaoInicialSerializer(required=False, many=True)
    logs = LogSolicitacoesUsuarioSerializer(many=True)

    class Meta:
        model = SolicitacaoMedicaoInicial
        exclude = ('id', 'criado_por',)


class SolicitacaoMedicaoInicialDashboardSerializer(serializers.ModelSerializer):
    escola = serializers.CharField(source='escola.nome')
    status = serializers.CharField(source='get_status_display')
    tipo_unidade = serializers.CharField(source='escola.tipo_unidade')
    log_mais_recente = serializers.SerializerMethodField()
    mes_ano = serializers.SerializerMethodField()

    def get_log_mais_recente(self, obj):
        return datetime.datetime.strftime(
            obj.log_mais_recente.criado_em, '%d/%m/%Y %H:%M') if obj.log_mais_recente else None

    def get_mes_ano(self, obj):
        return f'{converte_numero_em_mes(int(obj.mes))} {obj.ano}'

    class Meta:
        model = SolicitacaoMedicaoInicial
        fields = ('uuid', 'escola', 'mes_ano', 'tipo_unidade', 'status', 'log_mais_recente')


class ValorMedicaoSerializer(serializers.ModelSerializer):
    medicao_uuid = serializers.SerializerMethodField()
    medicao_alterado_em = serializers.SerializerMethodField()

    def get_medicao_uuid(self, obj):
        return obj.medicao.uuid

    def get_medicao_alterado_em(self, obj):
        if obj.medicao.alterado_em:
            return datetime.datetime.strftime(obj.medicao.alterado_em, '%d/%m/%Y, às %H:%M:%S')

    class Meta:
        model = ValorMedicao
        fields = ('categoria_medicao', 'nome_campo', 'valor', 'dia', 'medicao_uuid', 'uuid', 'medicao_alterado_em')


class CategoriaMedicaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoriaMedicao
        fields = '__all__'
