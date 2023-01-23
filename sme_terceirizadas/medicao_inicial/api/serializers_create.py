import json

import environ
from rest_framework import serializers

from sme_terceirizadas.cardapio.models import TipoAlimentacao
from sme_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from sme_terceirizadas.dados_comuns.utils import convert_base64_to_contentfile, update_instance_from_dict
from sme_terceirizadas.dados_comuns.validators import deve_ter_extensao_xls_xlsx_pdf
from sme_terceirizadas.escola.models import Escola, PeriodoEscolar, TipoUnidadeEscolar
from sme_terceirizadas.medicao_inicial.models import (
    AnexoOcorrenciaMedicaoInicial,
    CategoriaMedicao,
    DiaSobremesaDoce,
    GrupoMedicao,
    Medicao,
    Responsavel,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
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
        deve_ter_extensao_xls_xlsx_pdf(nome)
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
    anexos = AnexoOcorrenciaMedicaoInicialCreateSerializer(required=False, many=True)
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
        responsaveis_dict = self.context['request'].data.get('responsaveis', None)
        key_com_ocorrencias = validated_data.get('com_ocorrencias', None)

        validated_data.pop('responsaveis', None)
        update_instance_from_dict(instance, validated_data, save=True)

        if responsaveis_dict:
            responsaveis = json.loads(responsaveis_dict)
            instance.responsaveis.all().delete()
            for responsavel in responsaveis:
                Responsavel.objects.create(
                    solicitacao_medicao_inicial=instance,
                    nome=responsavel.get('nome', ''),
                    rf=responsavel.get('rf', '')
                )

        anexos_string = self.context['request'].data.get('anexos', None)
        if anexos_string:
            anexos = json.loads(anexos_string)
            for anexo in anexos:
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


class ValorMedicaoCreateUpdateSerializer(serializers.ModelSerializer):
    valor = serializers.CharField()
    nome_campo = serializers.CharField()
    categoria_medicao = serializers.SlugRelatedField(
        slug_field='id',
        required=True,
        queryset=CategoriaMedicao.objects.all(),
    )
    tipo_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        allow_null=True,
        queryset=TipoAlimentacao.objects.all()
    )
    medicao_uuid = serializers.SerializerMethodField()

    def get_medicao_uuid(self, obj):
        return obj.medicao.uuid

    class Meta:
        model = ValorMedicao
        exclude = ('id', 'medicao',)


class MedicaoCreateUpdateSerializer(serializers.ModelSerializer):
    solicitacao_medicao_inicial = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=SolicitacaoMedicaoInicial.objects.all()
    )
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='nome',
        required=True,
        queryset=PeriodoEscolar.objects.all(),
    )
    grupo = serializers.SlugRelatedField(
        slug_field='nome',
        required=False,
        queryset=GrupoMedicao.objects.all(),
    )
    valores_medicao = ValorMedicaoCreateUpdateSerializer(many=True, required=False)

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        valores_medicao_dict = validated_data.pop('valores_medicao', None)

        medicao = Medicao.objects.create(**validated_data)
        medicao.save()

        for valor_medicao in valores_medicao_dict:
            ValorMedicao.objects.create(
                medicao=medicao,
                dia=valor_medicao.get('dia', ''),
                valor=valor_medicao.get('valor', ''),
                nome_campo=valor_medicao.get('nome_campo', ''),
                categoria_medicao=valor_medicao.get('categoria_medicao', ''),
                tipo_alimentacao=valor_medicao.get('tipo_alimentacao', ''),
            )

        return medicao

    def update(self, instance, validated_data):  # noqa C901
        valores_medicao_dict = validated_data.pop('valores_medicao', None)
        uuids_criados_atualizados = []

        if valores_medicao_dict:
            for valor_medicao in valores_medicao_dict:
                valor_medicao_ = ValorMedicao.objects.update_or_create(
                    medicao=instance,
                    dia=valor_medicao.get('dia', ''),
                    nome_campo=valor_medicao.get('nome_campo', ''),
                    categoria_medicao=valor_medicao.get('categoria_medicao', ''),
                    tipo_alimentacao=valor_medicao.get('tipo_alimentacao', ''),
                    defaults={
                        'medicao': instance,
                        'dia': valor_medicao.get('dia', ''),
                        'valor': valor_medicao.get('valor', ''),
                        'nome_campo': valor_medicao.get('nome_campo', ''),
                        'categoria_medicao': valor_medicao.get('categoria_medicao', ''),
                        'tipo_alimentacao': valor_medicao.get('tipo_alimentacao', ''),
                    }
                )
                uuids_criados_atualizados.append(valor_medicao_[0].uuid)
        eh_observacao = self.context['request'].data.get('eh_observacao',)
        if not eh_observacao:
            instance.valores_medicao.filter(valor=0).delete()
        if uuids_criados_atualizados:
            instance.valores_medicao.exclude(uuid__in=uuids_criados_atualizados).delete()
        if not instance.valores_medicao.all().exists():
            instance.delete()

        return instance

    class Meta:
        model = Medicao
        exclude = ('id', 'criado_por',)
