import json

import environ
from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from sme_terceirizadas.dados_comuns.utils import convert_base64_to_contentfile, update_instance_from_dict
from sme_terceirizadas.dados_comuns.validators import deve_ter_extensao_xls_xlsx
from sme_terceirizadas.escola.models import Escola, TipoUnidadeEscolar
from sme_terceirizadas.medicao_inicial.models import (
    AnexoOcorrenciaMedicaoInicial,
    DiaSobremesaDoce,
    Responsavel,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao
)
from sme_terceirizadas.perfil.models import Usuario


class DiaSobremesaDoceCreateSerializer(serializers.ModelSerializer):
    tipo_unidade = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoUnidadeEscolar.objects.all(),
        required=True,
    )

    criado_por = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Usuario.objects.all(),
        required=True
    )

    class Meta:
        model = DiaSobremesaDoce
        exclude = ('id',)


class DiaSobremesaDoceCreateManySerializer(serializers.ModelSerializer):
    tipo_unidades = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoUnidadeEscolar.objects.all(),
        many=True,
        required=True,
    )

    def create(self, validated_data):
        """Cria ou atualiza dias de sobremesa doce."""
        dia_sobremesa_doce = None
        DiaSobremesaDoce.objects.filter(data=validated_data['data']).exclude(
            tipo_unidade__in=validated_data['tipo_unidades']).delete()
        dias_sobremesa_doce = DiaSobremesaDoce.objects.filter(data=validated_data['data'])
        for tipo_unidade in validated_data['tipo_unidades']:
            if not dias_sobremesa_doce.filter(tipo_unidade=tipo_unidade).exists():
                dia_sobremesa_doce = DiaSobremesaDoce(
                    criado_por=self.context['request'].user,
                    data=validated_data['data'],
                    tipo_unidade=tipo_unidade
                )
                dia_sobremesa_doce.save()
        return dia_sobremesa_doce

    class Meta:
        model = DiaSobremesaDoce
        fields = ('tipo_unidades', 'data', 'uuid')


class AnexoOcorrenciaMedicaoInicialCreateSerializer(serializers.ModelSerializer):
    arquivo = serializers.SerializerMethodField()
    nome = serializers.CharField()

    def get_arquivo(self, obj):
        env = environ.Env()
        api_url = env.str('URL_ANEXO', default='http://localhost:8000')
        return f'{api_url}{obj.arquivo.url}'

    def validate_nome(self, nome):
        deve_ter_extensao_xls_xlsx(nome)
        return nome

    class Meta:
        model = AnexoOcorrenciaMedicaoInicial
        exclude = ('id', 'solicitacao_medicao_inicial',)


class ResponsavelCreateSerializer(serializers.ModelSerializer):
    nome = serializers.CharField()
    rf = serializers.CharField()

    class Meta:
        model = Responsavel
        exclude = ('id', 'solicitacao_medicao_inicial',)


class SolicitacaoMedicaoInicialCreateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    tipo_contagem_alimentacoes = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=TipoContagemAlimentacao.objects.all(),
    )
    responsaveis = ResponsavelCreateSerializer(many=True)
    com_ocorrencias = serializers.BooleanField(required=False)
    anexo = AnexoOcorrenciaMedicaoInicialCreateSerializer(required=False)
    logs = LogSolicitacoesUsuarioSerializer(many=True, required=False)

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        responsaveis_dict = validated_data.pop('responsaveis', None)

        solicitacao = SolicitacaoMedicaoInicial.objects.create(**validated_data)
        solicitacao.save()

        for responsavel in responsaveis_dict:
            Responsavel.objects.create(
                solicitacao_medicao_inicial=solicitacao,
                nome=responsavel.get('nome', ''),
                rf=responsavel.get('rf', '')
            )

        solicitacao.inicia_fluxo(user=self.context['request'].user)
        return solicitacao

    def update(self, instance, validated_data):  # noqa C901
        responsaveis_dict = validated_data.pop('responsaveis', None)
        key_com_ocorrencias = validated_data.get('com_ocorrencias', None)

        update_instance_from_dict(instance, validated_data)

        if responsaveis_dict:
            instance.responsaveis.all().delete()
            for responsavel in responsaveis_dict:
                Responsavel.objects.create(
                    solicitacao_medicao_inicial=instance,
                    nome=responsavel.get('nome', ''),
                    rf=responsavel.get('rf', '')
                )

        anexo_string = self.context['request'].data.get('anexo', None)
        if anexo_string:
            anexo = json.loads(anexo_string)
            arquivo = convert_base64_to_contentfile(anexo.pop('base64'))
            AnexoOcorrenciaMedicaoInicial.objects.create(
                solicitacao_medicao_inicial=instance,
                arquivo=arquivo,
                nome=anexo.get('nome')
            )
        if key_com_ocorrencias is not None:
            instance.codae_encerra_medicao_inicial(user=self.context['request'].user)

        return instance

    class Meta:
        model = SolicitacaoMedicaoInicial
        exclude = ('id', 'criado_por',)
