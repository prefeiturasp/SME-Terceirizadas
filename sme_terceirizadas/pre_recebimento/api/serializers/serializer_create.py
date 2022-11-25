from datetime import date

from rest_framework import serializers

from sme_terceirizadas.dados_comuns.api.serializers import ContatoSerializer
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    EtapasDoCronograma,
    Laboratorio,
    ProgramacaoDoRecebimentoDoCronograma
)
from sme_terceirizadas.terceirizada.models import Terceirizada


class ProgramacaoDoRecebimentoDoCronogramaCreateSerializer(serializers.ModelSerializer):
    data_programada = serializers.CharField(required=False)
    tipo_carga = serializers.ChoiceField(
        choices=ProgramacaoDoRecebimentoDoCronograma.TIPO_CARGA_CHOICES, required=False, allow_blank=True)

    class Meta:
        model = ProgramacaoDoRecebimentoDoCronograma
        exclude = ('id', 'cronograma')


class EtapasDoCronogramaCreateSerializer(serializers.ModelSerializer):
    empenho_uuid = serializers.UUIDField(required=False)
    numero_empenho = serializers.CharField(required=False)
    etapa = serializers.CharField(required=False)
    parte = serializers.CharField(required=False)
    data_programada = serializers.CharField(required=False)
    quantidade = serializers.FloatField(required=False)
    total_embalagens = serializers.IntegerField(required=False)

    class Meta:
        model = EtapasDoCronograma
        exclude = ('id', 'cronograma')


class CronogramaCreateSerializer(serializers.ModelSerializer):
    armazem = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Terceirizada.objects.all(),
        allow_null=True
    )
    contrato_uuid = serializers.UUIDField(required=True)
    contrato = serializers.CharField(required=True)
    empresa_uuid = serializers.UUIDField(required=False)
    nome_empresa = serializers.CharField(required=False)
    produto_uuid = serializers.UUIDField(required=False)
    processo_sei = serializers.CharField(required=False)
    nome_produto = serializers.CharField(required=False)
    qtd_total_programada = serializers.FloatField(required=False)
    unidade_medida = serializers.CharField(required=False)
    tipo_embalagem = serializers.ChoiceField(
        choices=Cronograma.TIPO_EMBALAGEM_CHOICES, required=False, allow_blank=True)
    etapas = EtapasDoCronogramaCreateSerializer(many=True, required=False)
    programacoes_de_recebimento = ProgramacaoDoRecebimentoDoCronogramaCreateSerializer(many=True, required=False)
    cadastro_finalizado = serializers.BooleanField(required=False)

    def gera_proximo_numero_cronograma(self):
        ano = date.today().year
        ultimo_cronograma = Cronograma.objects.last()
        if ultimo_cronograma:
            return f'{str(int(ultimo_cronograma.numero[:3]) + 1).zfill(3)}/{ano}'
        else:
            return f'001/{ano}'

    def cria_etapas(self, etapas, cronograma):
        for etapa in etapas:
            EtapasDoCronograma.objects.create(
                cronograma=cronograma,
                **etapa
            )

    def cria_programacao(self, programacoes, cronograma):
        for programacao in programacoes:
            ProgramacaoDoRecebimentoDoCronograma.objects.create(
                cronograma=cronograma,
                **programacao
            )

    def create(self, validated_data):
        user = self.context['request'].user
        cadastro_finalizado = validated_data.pop('cadastro_finalizado', None)
        etapas = validated_data.pop('etapas', [])
        programacoes_de_recebimento = validated_data.pop('programacoes_de_recebimento', [])
        numero_cronograma = self.gera_proximo_numero_cronograma()
        cronograma = Cronograma.objects.create(numero=numero_cronograma, **validated_data)
        cronograma.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_CRIADO, usuario=user)

        self.cria_etapas(etapas, cronograma)
        self.cria_programacao(programacoes_de_recebimento, cronograma)

        if cadastro_finalizado:
            cronograma.inicia_fluxo(user=user)

        return cronograma

    def update(self, instance, validated_data):
        user = self.context['request'].user
        cadastro_finalizado = validated_data.pop('cadastro_finalizado', None)
        etapas = validated_data.pop('etapas', [])
        programacoes_de_recebimento = validated_data.pop('programacoes_de_recebimento', [])

        instance.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_CRIADO, usuario=user)
        instance.etapas.all().delete()
        instance.programacoes_de_recebimento.all().delete()

        update_instance_from_dict(instance, validated_data, save=True)

        self.cria_etapas(etapas, instance)
        self.cria_programacao(programacoes_de_recebimento, instance)

        if cadastro_finalizado:
            instance.inicia_fluxo(user=user)
        return instance

    class Meta:
        model = Cronograma
        exclude = ('id', 'numero', 'status')


class LaboratorioCreateSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(required=True)
    cnpj = serializers.CharField(required=True)
    cep = serializers.CharField(required=True)
    logradouro = serializers.CharField(required=True)
    numero = serializers.CharField(required=True)
    bairro = serializers.CharField(required=True)
    cidade = serializers.CharField(required=True)
    estado = serializers.CharField(required=True)
    credenciado = serializers.BooleanField(required=True)
    contatos = ContatoSerializer(many=True)

    def cria_contatos(self, contatos, laboratorio):
        for contato_json in contatos:
            contato = ContatoSerializer().create(
                validated_data=contato_json)
            laboratorio.contatos.add(contato)

    def create(self, validated_data):
        validated_data['nome'] = validated_data['nome'].upper()
        contatos = validated_data.pop('contatos', [])
        laboratorio = Laboratorio.objects.create(**validated_data)

        self.cria_contatos(contatos, laboratorio)
        return laboratorio

    def update(self, instance, validated_data):
        validated_data['nome'] = validated_data['nome'].upper()
        contatos = validated_data.pop('contatos', [])

        instance.contatos.all().delete()

        self.cria_contatos(contatos, instance)
        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = Laboratorio
        exclude = ('id', )
