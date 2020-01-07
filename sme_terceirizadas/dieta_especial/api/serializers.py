from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from ...dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ...dados_comuns.utils import convert_base64_to_contentfile
from ...dados_comuns.validators import deve_ser_no_passado
from ...escola.api.serializers import EscolaSimplesSerializer
from ..models import (
    AlergiaIntolerancia,
    Anexo,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    TipoDieta
)
from .validators import deve_ter_extensao_valida


class AnexoCreateSerializer(serializers.ModelSerializer):
    arquivo = serializers.CharField()
    nome = serializers.CharField()

    def validate_nome(self, nome):
        deve_ter_extensao_valida(nome)
        return nome

    class Meta:
        model = Anexo
        fields = ('arquivo', 'nome')


class AnexoSerializer(ModelSerializer):
    nome = serializers.CharField()

    class Meta:
        model = Anexo
        fields = ('arquivo', 'nome', 'eh_laudo_medico')


class SolicitacaoDietaEspecialCreateSerializer(serializers.ModelSerializer):
    anexos = serializers.ListField(
        child=AnexoCreateSerializer(), required=True
    )

    def validate_anexos(self, anexos):
        if not anexos:
            raise serializers.ValidationError('Anexos não pode ser vazio')
        return anexos

    def validate_data_nascimento_aluno(self, data_nascimento_aluno):
        deve_ser_no_passado(data_nascimento_aluno)
        return data_nascimento_aluno

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        anexos = validated_data.pop('anexos', [])
        solicitacao = SolicitacaoDietaEspecial.objects.create(**validated_data)

        for anexo in anexos:
            data = convert_base64_to_contentfile(anexo.get('arquivo'))
            anexo.pop('nome')
            Anexo.objects.create(
                solicitacao_dieta_especial=solicitacao, arquivo=data, eh_laudo_medico=True
            )

        solicitacao.inicia_fluxo(user=self.context['request'].user)
        return solicitacao

    class Meta:
        model = SolicitacaoDietaEspecial
        fields = (
            'uuid',
            'codigo_eol_aluno',
            'nome_completo_aluno',
            'nome_completo_pescritor',
            'registro_funcional_pescritor',
            'data_nascimento_aluno',
            'observacoes',
            'criado_em',
            'anexos'
        )


class SolicitacaoDietaEspecialSerializer(serializers.ModelSerializer):
    anexos = serializers.ListField(
        child=AnexoSerializer(), required=True
    )
    escola = EscolaSimplesSerializer()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    status_solicitacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )
    id_externo = serializers.CharField()

    class Meta:
        model = SolicitacaoDietaEspecial
        fields = (
            'uuid',
            'codigo_eol_aluno',
            'nome_completo_aluno',
            'nome_completo_pescritor',
            'registro_funcional_pescritor',
            'data_nascimento_aluno',
            'observacoes',
            'criado_em',
            'anexos',
            'status_solicitacao',
            'escola',
            'logs',
            'id_externo'
        )

class AlergiaIntoleranciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlergiaIntolerancia
        fields = ['descricao']

class ClassificacaoDietaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificacaoDieta
        fields = ['nome', 'descricao']

class MotivoNegacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoNegacao
        fields = ['descricao']

class TipoDietaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDieta
        fields = ['descricao']
